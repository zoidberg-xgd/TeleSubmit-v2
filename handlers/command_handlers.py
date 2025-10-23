"""
命令处理器模块
"""
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from database.db_manager import get_db
from utils.blacklist import (
    is_owner, 
    add_to_blacklist, 
    remove_from_blacklist, 
    get_blacklist, 
    is_blacklisted,
    _blacklist
)
from config.settings import OWNER_ID, NOTIFY_OWNER, TIMEOUT
from utils.database import get_user_state, get_all_user_states

logger = logging.getLogger(__name__)

async def cancel(update: Update, context: CallbackContext) -> int:
    """
    处理 /cancel 命令，取消当前会话
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        
    Returns:
        int: 结束会话状态
    """
    logger.info(f"收到 /cancel 命令，user_id: {update.effective_user.id}")
    user_id = update.effective_user.id
    try:
        async with get_db() as conn:
            c = await conn.cursor()
            await c.execute("DELETE FROM submissions WHERE user_id=?", (user_id,))
    except Exception as e:
        logger.error(f"取消时删除数据错误: {e}")
    await update.message.reply_text("❌ 投稿已取消")
    return ConversationHandler.END

async def debug(update: Update, context: CallbackContext):
    """
    调试命令，显示当前状态信息
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    logger.info(f"调试命令被调用: 用户ID={update.effective_user.id}")
    
    # 获取用户ID
    user_id = update.effective_user.id
    
    # 构建调试信息
    try:
        from config.settings import OWNER_ID, CHANNEL_ID, BOT_MODE, SHOW_SUBMITTER, NOTIFY_OWNER
        
        debug_info = (
            "🔍 **调试信息**\n\n"
            f"👤 您的用户ID: `{user_id}`\n"
            f"🤖 机器人所有者ID: `{OWNER_ID}`\n"
            f"✅ 您是所有者: {is_owner(user_id)}\n\n"
            f"📺 频道ID: {CHANNEL_ID}\n"
            f"🔄 机器人模式: {BOT_MODE}\n"
            f"👁️ 显示投稿人: {SHOW_SUBMITTER}\n"
            f"📲 通知所有者: {NOTIFY_OWNER}\n"
            f"⏱️ 会话超时: {TIMEOUT}秒\n\n"
            f"🗄️ 黑名单用户数: {len(_blacklist)}\n"
            f"📂 用户会话数: {len(get_all_user_states())}\n"
            f"🕒 服务器时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        
        # 获取系统信息
        import platform
        import psutil
        
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = process.cpu_percent(interval=0.1)
            uptime = (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds() / 60  # 分钟
            
            system_info = (
                "\n📊 **系统信息**\n\n"
                f"💻 操作系统: {platform.system()} {platform.release()}\n"
                f"🐍 Python版本: {platform.python_version()}\n"
                f"📈 CPU使用率: {cpu_percent:.1f}%\n"
                f"🧠 内存使用: {memory_usage:.1f} MB\n"
                f"⏲️ 运行时间: {int(uptime)} 分钟\n"
            )
            
            debug_info += system_info
        except Exception as e:
            logger.warning(f"获取系统信息失败: {e}")
            debug_info += "\n⚠️ 无法获取系统信息"
        
        try:
            # 尝试使用Markdown格式发送
            await update.message.reply_text(debug_info, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Markdown格式发送失败: {e}，尝试纯文本")
            try:
                # 如果Markdown失败，尝试纯文本
                plain_debug_info = debug_info.replace('**', '').replace('`', '')
                await update.message.reply_text(plain_debug_info)
            except Exception as e2:
                logger.error(f"发送调试信息失败: {e2}")
                await update.message.reply_text("❌ 发送调试信息失败")
    except Exception as e:
        logger.error(f"生成调试信息时发生错误: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ 生成调试信息时发生错误: {str(e)[:100]}")
        except Exception as e2:
            logger.error(f"发送错误消息失败: {e2}")

async def catch_all(update: Update, context: CallbackContext):
    """
    捕获所有未处理的消息
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    logger.debug(f"收到未知消息: {update}")

async def blacklist_add(update: Update, context: CallbackContext):
    """
    添加用户到黑名单
    
    命令格式: /blacklist_add <user_id> [reason]
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    logger.info(f"黑名单添加命令被调用: 用户ID={update.effective_user.id}")
    
    user_id = update.effective_user.id
    
    # 检查是否为所有者
    if not is_owner(user_id):
        logger.warning(f"非所有者用户 {user_id} 尝试使用黑名单添加命令")
        try:
            await update.message.reply_text("⚠️ 只有机器人所有者才能使用此命令")
        except Exception as e:
            logger.error(f"发送权限拒绝消息失败: {e}")
        return
    
    # 检查参数
    args = context.args
    if not args or len(args) < 1:
        try:
            await update.message.reply_text(
                "⚠️ 命令格式错误\n\n"
                "正确格式: /blacklist_add <用户ID> [原因]\n"
                "例如: /blacklist_add 123456789 发送垃圾内容\n\n"
                "用户ID必须是数字，可以通过用户的投稿通知获取"
            )
        except Exception as e:
            logger.error(f"发送格式提示消息失败: {e}")
        return
    
    try:
        target_user_id = int(args[0])
        reason = " ".join(args[1:]) if len(args) > 1 else "未指定原因"
        
        # 添加到黑名单
        success = await add_to_blacklist(target_user_id, reason)
        if success:
            try:
                await update.message.reply_text(f"✅ 已将用户 {target_user_id} 添加到黑名单\n原因: {reason}")
                logger.info(f"用户 {user_id} 成功将 {target_user_id} 添加到黑名单，原因: {reason}")
            except Exception as e:
                logger.error(f"发送成功消息失败: {e}")
        else:
            try:
                await update.message.reply_text(f"❌ 添加用户 {target_user_id} 到黑名单时出错")
            except Exception as e:
                logger.error(f"发送失败消息失败: {e}")
    except ValueError:
        try:
            await update.message.reply_text(
                "⚠️ 用户ID格式错误\n\n"
                "用户ID必须是数字（例如：123456789）\n"
                "您可以从投稿通知消息中获取用户ID，或者使用 @userinfobot 机器人查询"
            )
        except Exception as e:
            logger.error(f"发送ID格式错误消息失败: {e}")
    except Exception as e:
        logger.error(f"处理黑名单添加命令时出错: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ 处理命令时发生错误: {str(e)[:100]}")
        except Exception as e2:
            logger.error(f"发送错误消息失败: {e2}")

async def blacklist_remove(update: Update, context: CallbackContext):
    """
    从黑名单中移除用户
    
    命令格式: /blacklist_remove <user_id>
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    logger.info(f"黑名单移除命令被调用: 用户ID={update.effective_user.id}")
    
    user_id = update.effective_user.id
    
    # 检查是否为所有者
    if not is_owner(user_id):
        logger.warning(f"非所有者用户 {user_id} 尝试使用黑名单移除命令")
        try:
            await update.message.reply_text("⚠️ 只有机器人所有者才能使用此命令")
        except Exception as e:
            logger.error(f"发送权限拒绝消息失败: {e}")
        return
    
    # 检查参数
    args = context.args
    if not args or len(args) < 1:
        try:
            await update.message.reply_text(
                "⚠️ 命令格式错误\n\n"
                "正确格式: /blacklist_remove <用户ID>\n"
                "例如: /blacklist_remove 123456789\n\n"
                "用户ID必须是数字，可以通过 /blacklist_list 命令查看所有黑名单用户"
            )
        except Exception as e:
            logger.error(f"发送格式提示消息失败: {e}")
        return
    
    try:
        target_user_id = int(args[0])
        
        # 从黑名单中移除
        success = await remove_from_blacklist(target_user_id)
        if success:
            try:
                await update.message.reply_text(f"✅ 已将用户 {target_user_id} 从黑名单中移除")
                logger.info(f"用户 {user_id} 成功将 {target_user_id} 从黑名单中移除")
            except Exception as e:
                logger.error(f"发送成功消息失败: {e}")
        else:
            try:
                await update.message.reply_text(f"❓ 用户 {target_user_id} 不在黑名单中")
            except Exception as e:
                logger.error(f"发送失败消息失败: {e}")
    except ValueError:
        try:
            await update.message.reply_text(
                "⚠️ 用户ID格式错误\n\n"
                "用户ID必须是数字（例如：123456789）\n"
                "请使用 /blacklist_list 命令查看所有黑名单用户的ID"
            )
        except Exception as e:
            logger.error(f"发送ID格式错误消息失败: {e}")
    except Exception as e:
        logger.error(f"处理黑名单移除命令时出错: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ 处理命令时发生错误: {str(e)[:100]}")
        except Exception as e2:
            logger.error(f"发送错误消息失败: {e2}")

async def blacklist_list(update: Update, context: CallbackContext):
    """
    列出所有黑名单用户
    
    命令格式: /blacklist_list
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    logger.info(f"黑名单列表命令被调用: 用户ID={update.effective_user.id}")
    
    user_id = update.effective_user.id
    
    # 检查是否为所有者
    if not is_owner(user_id):
        logger.warning(f"非所有者用户 {user_id} 尝试使用黑名单列表命令")
        try:
            await update.message.reply_text("⚠️ 只有机器人所有者才能使用此命令")
        except Exception as e:
            logger.error(f"发送权限拒绝消息失败: {e}")
        return
    
    try:
        # 获取黑名单
        blacklist = await get_blacklist()
        
        if not blacklist:
            try:
                await update.message.reply_text("📋 黑名单为空")
                logger.info("黑名单为空，返回空列表")
            except Exception as e:
                logger.error(f"发送空黑名单消息失败: {e}")
            return
        
        # 格式化黑名单消息
        message = "📋 **黑名单用户列表**:\n\n"
        for i, user in enumerate(blacklist, 1):
            message += f"{i}. ID: `{user['user_id']}`\n"
            message += f"   原因: {user['reason']}\n"
            message += f"   添加时间: {user['added_at']}\n\n"
        
        try:
            # 尝试带Markdown格式发送
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"成功发送黑名单列表给用户 {user_id}")
        except Exception as e:
            logger.warning(f"Markdown格式发送失败: {e}，尝试纯文本")
            try:
                # 如果Markdown失败，尝试纯文本
                plain_message = message.replace('**', '').replace('`', '')
                await update.message.reply_text(plain_message)
                logger.info(f"成功以纯文本格式发送黑名单列表给用户 {user_id}")
            except Exception as e2:
                logger.error(f"发送黑名单列表失败: {e2}")
    except Exception as e:
        logger.error(f"处理黑名单列表命令时出错: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ 获取黑名单时发生错误: {str(e)[:100]}")
        except Exception as e2:
            logger.error(f"发送错误消息失败: {e2}")