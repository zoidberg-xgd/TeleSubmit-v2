"""
错误处理模块
"""
import logging
import asyncio
import traceback
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram.error import (
    TelegramError, 
    Forbidden, 
    NetworkError, 
    BadRequest,
    TimedOut,
    ChatMigrated,
    RetryAfter,
    InvalidToken
)

logger = logging.getLogger(__name__)

# 最大重试次数
MAX_RETRY_ATTEMPTS = 3

async def error_handler(update: Update, context: CallbackContext) -> None:
    """
    处理程序错误的全局处理函数
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    # 提取错误信息
    error = context.error
    error_type = type(error).__name__
    error_msg = str(error)
    
    # 记录错误
    logger.error(f"处理更新时发生异常 - 类型:{error_type}, 消息:{error_msg}")
    
    # 记录用户信息（如果有）
    if update and update.effective_user:
        user_id = update.effective_user.id
        username = update.effective_user.username or "未设置"
        logger.error(f"错误涉及用户: 用户ID: {user_id}, 用户名: @{username}")
    
    # 记录更新信息（如果有）
    if update:
        # 检查是否是回调查询
        if update.callback_query:
            logger.error(f"错误发生在回调查询处理中，回调数据: {update.callback_query.data}")
            
            # 如果是回调查询中的NoneType错误，尝试恢复
            if error_type == "TypeError" and "NoneType" in error_msg and "await" in error_msg:
                logger.warning("检测到回调查询中的NoneType错误，尝试恢复...")
                try:
                    # 确认回调查询以防止界面阻塞
                    await update.callback_query.answer()
                    await update.effective_chat.send_message(
                        "操作已完成，请继续按照提示操作。如遇问题，请发送 /cancel 取消当前会话，然后重新开始。"
                    )
                    return
                except Exception as e:
                    logger.error(f"尝试恢复失败: {e}")
    
    # 对于一些已知类型的错误进行分类处理
    if "Unauthorized" in error_msg or "forbidden" in error_msg.lower() or "user is deactivated" in error_msg.lower():
        # 用户已阻止机器人
        logger.warning(f"用户已阻止机器人或无权访问: {error}")
        return
    
    elif isinstance(error, BadRequest):
        # Telegram API错误
        if "Message is not modified" in error_msg:
            # 消息未修改错误，可以忽略
            logger.debug("忽略消息未修改错误")
            return
        
        if "Query is too old" in error_msg:
            # 回调查询过期，可以忽略
            logger.debug("忽略回调查询过期错误")
            if update and update.callback_query:
                try:
                    await update.callback_query.answer("此操作已过期，请重新尝试")
                except:
                    pass
            return
    
    # 对于其他错误，尝试通知用户（如果可能）
    if update and update.effective_chat:
        try:
            await update.effective_chat.send_message(
                "❌ 抱歉，处理您的请求时发生了错误。请稍后再试，或发送 /cancel 取消当前会话，然后发送 /start 重新开始。"
            )
        except Exception as e:
            logger.error(f"发送错误通知失败: {e}")
    
    # 记录详细的堆栈跟踪
    tb_list = traceback.format_exception(None, error, error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"完整的堆栈跟踪:\n{tb_string}")
    
    # 可选：向开发者发送错误报告
    if False:  # 设置为True以启用向开发者发送错误报告
        # 安全地构建错误消息
        message = (
            f"发生异常\n"
            f"<pre>update = {html.escape(str(update) if isinstance(update, object) else 'No update')}"
            f"</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        
        # 将错误记录到文件或发送到监控系统
        # 例如: await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode='HTML')

async def handle_timeout_error(update, context):
    """处理超时错误"""
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ 网络请求超时，请稍等片刻再试。如果问题持续，请发送 /start 重新开始。"
            )
        except Exception as e:
            logger.error(f"回复超时错误消息失败: {e}")

async def handle_bad_request(update, context, error):
    """处理错误请求"""
    if isinstance(update, Update) and update.effective_message:
        try:
            # 检查常见的 BadRequest 错误
            error_text = str(error).lower()
            
            if "message is not modified" in error_text:
                # 消息未修改，忽略即可
                logger.info("忽略'消息未修改'错误")
                return
            elif "message to edit not found" in error_text:
                logger.info("忽略'未找到要编辑的消息'错误")
                return
            elif "query is too old" in error_text:
                await update.effective_message.reply_text(
                    "此操作已过期，请重新开始。"
                )
            elif "have no rights" in error_text or "not enough rights" in error_text:
                await update.effective_message.reply_text(
                    "机器人权限不足，无法执行此操作。请联系管理员。"
                )
            else:
                await update.effective_message.reply_text(
                    "⚠️ 请求格式错误，请检查输入并重试。"
                )
        except Exception as e:
            logger.error(f"回复 BadRequest 错误消息失败: {e}")

async def handle_forbidden_error(update, context, error):
    """处理禁止访问错误"""
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ 机器人无权执行此操作。可能是权限不足或被用户阻止。"
            )
        except Exception as e:
            logger.error(f"回复 Forbidden 错误消息失败: {e}")

async def handle_network_error(update, context, error):
    """处理网络错误"""
    # 记录网络错误但不一定向用户显示
    logger.warning(f"发生网络错误: {error}")
    
    # 分析网络错误类型
    error_msg = str(error).lower()
    
    # 检查网络错误的具体类型
    if isinstance(error, TimedOut):
        retry_msg = "操作超时，请稍后再试。"
    elif "connection" in error_msg and "reset" in error_msg:
        retry_msg = "网络连接被重置，请稍后重试。"
    elif "proxy" in error_msg:
        retry_msg = "代理连接问题，请检查网络设置。"
    elif "ssl" in error_msg:
        retry_msg = "安全连接问题，请稍后再试。"
    else:
        retry_msg = "网络连接出现问题，请稍后再试。"
    
    # 尝试重新连接或简单通知用户
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(f"⚠️ {retry_msg}")
        except Exception as e:
            logger.error(f"回复网络错误消息失败: {e}")
            # 最后尝试通过其他方式发送
            try:
                if update.effective_chat:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"⚠️ 网络问题，请稍后再试。"
                    )
            except:
                pass

async def handle_retry_after(update, context, error):
    """处理需要重试的错误"""
    retry_seconds = error.retry_after
    logger.warning(f"接收到限流通知，需等待 {retry_seconds} 秒后重试")
    
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"⚠️ 机器人被限流，请在 {retry_seconds} 秒后重试。"
            )
        except Exception as e:
            logger.error(f"回复限流错误消息失败: {e}")

async def handle_general_error(update, context, error):
    """处理一般性错误"""
    if isinstance(update, Update) and update.effective_message:
        try:
            # 创建错误报告按钮
            keyboard = [
                [InlineKeyboardButton("重试", callback_data="retry_last_action")],
                [InlineKeyboardButton("重新开始", callback_data="restart")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.effective_message.reply_text(
                "⚠️ 对话处理过程中发生错误，请稍后再试或重新开始。\n"
                "如果问题持续出现，请联系管理员。",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"回复一般错误消息失败: {e}")
            # 最后的尝试 - 非常简单的消息
            try:
                await update.effective_message.reply_text("⚠️ 出现错误，请重新开始对话。")
            except:
                pass