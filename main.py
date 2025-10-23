"""
Telegram 投稿机器人主程序
支持媒体和文档投稿
"""
import sys
import json
import signal
import asyncio
import platform
import logging
import os
from datetime import datetime, time as datetime_time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
    ApplicationHandlerStop,
    CallbackQueryHandler
)
from dotenv import load_dotenv

# 配置相关导入
from config.settings import TOKEN, TIMEOUT, BOT_MODE, MODE_MEDIA, MODE_DOCUMENT, MODE_MIXED
from models.state import STATE

# 数据库相关导入
from database.db_manager import init_db, cleanup_old_data, get_db
from utils.database import (
    get_user_state, 
    delete_user_state, 
    is_blacklisted, 
    initialize_database
)

# 工具函数导入
from utils.logging_config import setup_logging, cleanup_old_logs
from utils.helper_functions import CONFIG

# 处理程序导入 - 按功能分组
# 基础命令
from handlers import (
    start, help_command, cancel, settings, settings_callback,
    handle_text, collect_extra, handle_image, done_image,
    handle_document, done_document, switch_to_doc_mode
)

# 黑名单管理
from utils.blacklist import manage_blacklist, init_blacklist, blacklist_filter
from handlers.command_handlers import blacklist_add, blacklist_remove, blacklist_list, catch_all, debug

# 投稿处理
from handlers.publish import publish_submission

# 不同投稿模式支持
from handlers.mode_selection import select_mode
from handlers.document_handlers import handle_doc, done_doc, prompt_doc
from handlers.media_handlers import handle_media, done_media, skip_media, prompt_media
from handlers.submit_handlers import (
    handle_tag, 
    handle_link, 
    handle_title, 
    handle_note, 
    handle_spoiler,
    skip_optional_link,
    skip_optional_title,
    skip_optional_note
)

# 错误处理
from handlers.error_handler import error_handler

# 设置日志
logger = logging.getLogger(__name__)
setup_logging()

# 加载环境变量
load_dotenv()

# 全局变量
TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT", "900"))  # 默认15分钟

# 黑名单过滤函数包装器
def check_blacklist(handler_func):
    """黑名单过滤函数包装器"""
    async def wrapper(update, context):
        # 先进行黑名单检查
        if not blacklist_filter(update):
            # 如果在黑名单中，直接返回
            return
        # 不在黑名单中，调用原始处理函数
        return await handler_func(update, context)
    return wrapper

# 会话超时检查函数
async def check_conversation_timeout(update: Update, context: CallbackContext) -> None:
    """
    检查会话是否超时的处理函数
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    # 对命令消息进行特殊处理 - 命令直接通过，不检查超时
    if update.message and update.message.text and update.message.text.startswith('/'):
        command = update.message.text.split()[0]  # 获取命令部分
        logger.debug(f"跳过命令消息的超时检查: {command}")
        # 关键点：对于命令消息，不进行任何阻止，直接通过
        return
    
    # 检查用户是否在黑名单中
    if is_blacklisted(user_id):
        logger.warning(f"黑名单用户 {user_id} 尝试发送消息")
        await update.message.reply_text("❌ 您已被列入黑名单，无法使用此机器人。")
        return ApplicationHandlerStop()
    
    # 尝试获取用户会话状态
    try:
        user_state = get_user_state(user_id)
        
        # 如果用户没有会话，允许正常流程继续
        if not user_state:
            logger.debug(f"用户 {user_id} 没有活跃会话，不检查超时")
            return
        
        # 检查超时
        import time
        current_time = time.time()
        last_activity = user_state.get("last_activity", 0)
        time_diff = current_time - last_activity
        
        if time_diff > TIMEOUT_SECONDS:
            logger.info(f"用户 {user_id} 会话超时 ({time_diff:.2f}秒 > {TIMEOUT_SECONDS}秒)")
            
            # 删除用户会话数据
            delete_user_state(user_id)
            
            # 向用户发送超时通知
            try:
                await update.message.reply_text(
                    "⏱️ 您的会话已超时。请发送 /start 重新开始。"
                )
            except Exception as e:
                logger.error(f"发送超时通知失败: {e}")
            
            return ApplicationHandlerStop()
        
        logger.debug(f"用户 {user_id} 会话活跃 ({time_diff:.2f}秒 < {TIMEOUT_SECONDS}秒)")
    except Exception as e:
        logger.error(f"检查会话超时时发生错误: {e}")
        # 出错时不阻止消息处理继续，而是让正常流程继续
    
    return

# 添加全局更新记录器
async def log_all_updates(update: Update, context: CallbackContext) -> None:
    """记录所有接收到的更新"""
    if update.message and update.message.text:
        logger.info(f"收到命令: {update.message.text} 来自用户: {update.effective_user.id}")
    return None  # 允许更新继续传递给其他处理器

async def main():
    """
    主函数 - 设置并启动机器人
    """
    logger.info(f"启动TeleSubmit机器人。版本: {CONFIG.get('VERSION', '0.1.0')}")
    logger.info(f"会话超时时间: {TIMEOUT_SECONDS}秒")
    
    # 初始化数据库
    await init_db()
    # 初始化用户会话数据库
    initialize_database()
    # 初始化黑名单
    await init_blacklist()
    
    # 创建和启动应用程序
    token = TOKEN
    if not token:
        logger.error("未设置TELEGRAM_BOT_TOKEN环境变量")
        sys.exit(1)
        
    # 创建Application实例
    application = Application.builder().token(token).build()
    
    # 设置应用程序
    setup_application(application)
    
    # 使用start_polling方法而不是run_polling
    logger.info("机器人正在启动，使用Ctrl+C停止")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=None)
    
    # 添加事件处理器以便优雅关闭
    loop = asyncio.get_running_loop()
    stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)
    for s in stop_signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(application, s, loop))
        )
        
    # 保持应用程序运行
    await asyncio.Event().wait()
    
    logger.info("机器人已停止")


async def shutdown(application, signal, loop):
    """
    优雅地关闭机器人
    """
    logger.info(f"收到信号 {signal.name}，正在关闭...")
    
    # 关闭机器人更新器
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    
    # 结束事件循环
    loop.stop()


def setup_application(application):
    """
    初始化和配置应用程序
    """
    # 首先设置全局记录器为最高优先级
    application.add_handler(MessageHandler(filters.ALL, log_all_updates), group=-999)
    
    # 添加黑名单管理命令和调试命令（设置为最高优先级，不可被其他处理器拦截）
    try:
        logger.info("注册高优先级命令处理器...")
        application.add_handler(CommandHandler('debug', debug), group=-998)
        application.add_handler(CommandHandler('blacklist_add', blacklist_add), group=-998)
        application.add_handler(CommandHandler('blacklist_remove', blacklist_remove), group=-998)
        application.add_handler(CommandHandler('blacklist_list', blacklist_list), group=-998)
        # 不再注册高优先级的cancel命令，只在ConversationHandler的fallbacks中注册
        # application.add_handler(CommandHandler('cancel', cancel), group=-998)  # 注释掉这行
        logger.info("高优先级命令处理器注册完成")
    except Exception as e:
        logger.error(f"注册高优先级命令处理器失败: {e}", exc_info=True)
    
    # 注册错误处理
    application.add_error_handler(error_handler)
    
    # 注册基本命令处理器
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("blacklist", manage_blacklist), group=1)
    
    # 注册会话超时检查处理器
    application.add_handler(MessageHandler(filters.ALL, check_conversation_timeout), group=0)
    
    try:
        # 添加会话处理器
        logger.info("注册会话处理器...")
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("submit", start),
                CommandHandler("start", start)  # 确保/start也是入口点
            ],
            states={
                # 模式选择状态
                STATE.get('START_MODE', 0): [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, select_mode)
                ],
                
                # 文档和媒体处理状态 - 优先处理skip_media命令
                STATE.get('MEDIA', 2): [
                    CommandHandler('done_media', done_media),
                    CommandHandler('skip_media', skip_media),
                    MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.AUDIO |
                                 filters.Document.Category("animation") | filters.Document.AUDIO, 
                                 handle_media),
                    # 在媒体状态下也检查文档类型
                    MessageHandler(filters.Document.ALL, handle_media),
                    # 添加媒体模式切换回调
                    CallbackQueryHandler(switch_to_doc_mode, pattern="^switch_to_doc$"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, prompt_media)
                ],
                STATE.get('DOC', 1): [
                    CommandHandler('done_doc', done_doc),
                    MessageHandler(filters.Document.ALL, handle_doc),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, prompt_doc)
                ],
                
                # 其他状态
                STATE.get('TEXT', 10): [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                STATE.get('IMAGE', 11): [
                    MessageHandler(filters.PHOTO | filters.CAPTION, handle_image),
                    CommandHandler("done_img", done_image)
                ],
                STATE.get('EXTRA', 12): [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_extra)],
                STATE.get('PUBLISH', 13): [
                    CallbackQueryHandler(publish_submission, pattern="^publish$"),
                    CallbackQueryHandler(cancel, pattern="^cancel$")
                ],
                
                # 投稿处理状态
                STATE.get('TAG', 4): [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tag)],
                STATE.get('LINK', 5): [
                    CommandHandler('skip_optional', skip_optional_link),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
                ],
                STATE.get('TITLE', 6): [
                    CommandHandler('skip_optional', skip_optional_title),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)
                ],
                STATE.get('NOTE', 7): [
                    CommandHandler('skip_optional', skip_optional_note),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_note)
                ],
                STATE.get('SPOILER', 8): [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_spoiler)]
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            name="submission_conversation",
            persistent=False,
        )
        
        application.add_handler(conv_handler, group=2)
        logger.info("会话处理器注册完成")
    except Exception as e:
        logger.error(f"注册会话处理器失败: {e}", exc_info=True)
    
    # 添加回调查询处理器
    application.add_handler(CallbackQueryHandler(settings_callback), group=3)
    
    # 添加周期性清理任务
    try:
        logger.info("设置定期任务...")
        job_queue = application.job_queue
        job_queue.run_repeating(
            lambda context: asyncio.create_task(cleanup_old_data()), 
            interval=300, 
            first=10
        )
        
        # 添加周期性清理日志任务
        def clean_logs_job(context):
            """定期清理日志文件"""
            logger.info("执行定期日志清理任务")
            cleanup_old_logs("logs")
            
        # 每天凌晨3点执行一次日志清理
        job_queue.run_daily(clean_logs_job, time=datetime_time(hour=3, minute=0))
        logger.info("定期任务设置完成")
    except Exception as e:
        logger.error(f"设置定期任务失败: {e}", exc_info=True)
    
    # 添加未处理消息的捕获处理器 (最低优先级组)
    application.add_handler(MessageHandler(filters.ALL, catch_all), group=999)
    
    logger.info("应用程序设置完成")


if __name__ == "__main__":
    try:
        # 根据系统设置正确的事件循环策略
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # 确保使用新的事件循环
        asyncio.set_event_loop(asyncio.new_event_loop())
        
        # 启动主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序中断，正在退出...")
    except Exception as e:
        logger.error(f"发生异常: {e}", exc_info=True)
        sys.exit(1)