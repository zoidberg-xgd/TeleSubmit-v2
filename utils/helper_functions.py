"""
工具函数模块
"""
import re
import json
import asyncio
import logging
from functools import lru_cache, wraps
from datetime import datetime
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from config.settings import ALLOWED_TAGS, NET_TIMEOUT, SHOW_SUBMITTER
from database.db_manager import get_db

logger = logging.getLogger(__name__)

# 标签分割正则表达式
TAG_SPLIT_PATTERN = re.compile(r'[,\s，]+')

# 配置常量
CONFIG = {
    "VERSION": "1.0.0",
    "MAX_MEDIA_COUNT": 10,
    "MAX_DOCUMENT_COUNT": 10,
    "NET_TIMEOUT": 30,  # 网络超时时间（秒）
    "MAX_RETRIES": 3,   # 最大重试次数
    "RETRY_DELAY": 2,   # 重试延迟（秒）
}

@lru_cache(maxsize=128)
def process_tags(raw_tags: str) -> tuple:
    """
    处理标签字符串
    
    Args:
        raw_tags: 原始标签字符串
        
    Returns:
        tuple: (成功标志, 处理后的标签字符串)
    """
    try:
        # 使用预编译的正则表达式分割标签
        tags = [t.strip().lower() for t in TAG_SPLIT_PATTERN.split(raw_tags) if t.strip()]
        tags = tags[:ALLOWED_TAGS]
        
        # 确保每个标签前加上#，如果标签已经有#，则不重复添加
        processed = [f"#{tag}" if not tag.startswith("#") else tag for tag in tags]
        
        # 处理标签长度超过30的情况
        processed = [tag[:30] if len(tag) > 0 else tag for tag in processed]
        
        # 使用空格拼接标签，得到正确的格式
        return True, ' '.join(processed)
    except Exception as e:
        logger.error(f"标签处理错误: {e}")
        return False, ""

def escape_markdown(text: str) -> str:
    """
    转义 HTML 中的特殊字符
    
    Args:
        text: 需要转义的文本
        
    Returns:
        str: 转义后的文本
    """
    escape_chars = r'\_*[]()~>#+-=|{}.!'
    return ''.join(f"\\{c}" if c in escape_chars else c for c in text)

def build_caption(data) -> str:
    """
    构建媒体说明文本
    
    Args:
        data: 包含投稿信息的数据对象
        
    Returns:
        str: 格式化的说明文本
    """
    MAX_CAPTION_LENGTH = 1024  # Telegram 的最大 caption 长度

    def get_link_part(link: str) -> str:
        return f"🔗 链接： {link}" if link else ""
    
    def get_title_part(title: str) -> str:
        return f"🔖 标题： \n【{title}】" if title else ""
    
    def get_note_part(note: str) -> str:
        # "简介"部分要求第一行为标签，后面跟内容
        return f"📝 简介：\n{note}" if note else ""
    
    def get_tags_part(tags: str) -> str:
        return f"🏷 Tags: {tags}" if tags else ""
    
    def get_spoiler_part(spoiler: str) -> str:
        return "⚠️点击查看⚠️" if spoiler.lower() == "true" else ""
    
    def get_submitter_part(user_id: int) -> str:
        if not SHOW_SUBMITTER:
            return ""
        
        # 获取保存的用户名，如果存在的话
        # sqlite3.Row对象不支持get()方法，使用try-except处理
        try:
            username = data["username"] if "username" in data else f"user{user_id}"
        except (KeyError, TypeError):
            username = f"user{user_id}"
        
        # 构建用户链接，可以通过点击访问用户资料
        return f"\n\n投稿人：<a href=\"tg://user?id={user_id}\">@{username}</a>"

    # 收集各部分，只有内容不为空时才添加，避免产生多余的换行
    parts = []
    
    # 安全获取属性，防止访问不存在的键
    try:
        link = get_link_part(data["link"] if data["link"] else "")
        if link:
            parts.append(link)
    except (KeyError, TypeError):
        pass

    try:
        title = get_title_part(data["title"] if data["title"] else "")
        if title:
            parts.append(title)
    except (KeyError, TypeError):
        pass

    try:
        note = get_note_part(data["note"] if data["note"] else "")
        if note:
            parts.append(note)
    except (KeyError, TypeError):
        pass

    try:
        tags = get_tags_part(data["tags"] if data["tags"] else "")
        if tags:
            parts.append(tags)
    except (KeyError, TypeError):
        pass
    
    # 将各部分按换行符连接，避免空值带来多余换行
    caption_body = "\n".join(parts)
    
    try:
        spoiler = get_spoiler_part(data["spoiler"] if data["spoiler"] else "false")
    except (KeyError, TypeError):
        spoiler = ""
    
    # 添加投稿人信息（如果启用）
    try:
        submitter = get_submitter_part(data["user_id"])
    except (KeyError, TypeError):
        submitter = ""
    
    # 如果存在正文内容且有剧透提示，则剧透提示单独占一行
    if caption_body:
        full_caption = f"{spoiler}\n{caption_body}{submitter}" if spoiler else f"{caption_body}{submitter}"
    else:
        full_caption = f"{spoiler}{submitter}" if submitter else spoiler

    # 如果整体长度在允许范围内，则直接返回
    if len(full_caption) <= MAX_CAPTION_LENGTH:
        return full_caption

    # 超长情况：保留投稿人信息，尝试截断 note 部分（其他部分保持不变）
    fixed_parts = []
    if link:
        fixed_parts.append(link)
    if title:
        fixed_parts.append(title)
    if tags:
        fixed_parts.append(tags)
    fixed_text = "\n".join(fixed_parts)
    
    # 预留剧透提示、投稿人信息和固定部分所占长度以及连接换行符
    prefix = f"{spoiler}\n" if spoiler and fixed_text else spoiler
    # 计算可用长度（要为投稿人信息预留空间）
    connector = "\n" if fixed_text and note else ""
    available_length = MAX_CAPTION_LENGTH - len(prefix) - len(fixed_text) - len(connector) - len(submitter)
    
    try:
        truncated_note = (data["note"][:available_length] + "...") if (available_length > 0 and data["note"]) else ""
    except (KeyError, TypeError):
        truncated_note = ""
        
    truncated_note_part = get_note_part(truncated_note)
    
    # 重新组装各部分
    parts = []
    if link:
        parts.append(link)
    if title:
        parts.append(title)
    if truncated_note_part:
        parts.append(truncated_note_part)
    if tags:
        parts.append(tags)
    caption_body = "\n".join(parts)
    full_caption = f"{spoiler}\n{caption_body}{submitter}" if spoiler and caption_body else f"{spoiler or caption_body}{submitter}"

    return full_caption[:MAX_CAPTION_LENGTH]

def validate_state(expected_state: int):
    """
    验证会话状态装饰器
    
    Args:
        expected_state: 期望的状态值
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            try:
                async with get_db() as conn:
                    c = await conn.cursor()
                    await c.execute("SELECT timestamp FROM submissions WHERE user_id=?", (user_id,))
                    result = await c.fetchone()
                    if not result:
                        await update.message.reply_text("❌ 会话已过期，请重新发送 /start")
                        return ConversationHandler.END
            except Exception as e:
                logger.error(f"状态验证错误: {e}")
                await update.message.reply_text("❌ 内部错误，请稍后再试")
                return ConversationHandler.END
            return await func(update, context)
        return wrapper
    return decorator

async def safe_send(send_func, *args, **kwargs):
    """
    安全发送函数，包含重试逻辑
    
    Args:
        send_func: 发送函数
        args: 位置参数
        kwargs: 关键字参数
        
    Returns:
        发送结果或None（如果失败）
    """
    max_retries = 2  # 最多重试次数
    current_attempt = 0
    last_error = None
    
    while current_attempt <= max_retries:
        try:
            return await asyncio.wait_for(send_func(*args, **kwargs), timeout=NET_TIMEOUT)
        except asyncio.TimeoutError:
            current_attempt += 1
            last_error = f"网络请求超时 (尝试 {current_attempt}/{max_retries + 1})"
            # 只有在最后一次尝试失败时才记录
            if current_attempt > max_retries:
                logger.warning(last_error)
            else:
                # 非最后一次尝试，只打印调试信息
                logger.debug(f"发送超时，正在重试 ({current_attempt}/{max_retries + 1})...")
                await asyncio.sleep(2)  # 等待2秒后重试
        except Exception as e:
            # 其他错误直接记录
            last_error = str(e)
            logger.error(f"发送失败: {e}")
            return None
    
    # 所有重试都失败，但我们不想中断流程，所以返回 None
    return None

# 增强型安全发送函数
async def enhanced_safe_send(send_func, *args, **kwargs):
    """
    增强型安全发送函数，提供更全面的错误处理和重试逻辑
    
    Args:
        send_func: 发送函数
        args: 位置参数
        kwargs: 关键字参数
        
    Returns:
        发送结果或None（如果失败）
    """
    max_retries = CONFIG["MAX_RETRIES"]
    base_delay = CONFIG["RETRY_DELAY"]
    current_attempt = 0
    last_error = None
    
    while current_attempt <= max_retries:
        try:
            return await asyncio.wait_for(send_func(*args, **kwargs), timeout=NET_TIMEOUT)
        except asyncio.TimeoutError:
            current_attempt += 1
            last_error = f"网络请求超时 (尝试 {current_attempt}/{max_retries + 1})"
            
            if current_attempt <= max_retries:
                # 使用指数退避算法
                delay = base_delay * (2 ** (current_attempt - 1))
                logger.info(f"发送超时，将在 {delay} 秒后重试 ({current_attempt}/{max_retries})...")
                await asyncio.sleep(delay)
            else:
                logger.warning(f"发送失败: {last_error}")
        
        except Exception as e:
            error_text = str(e).lower()
            
            # 处理Markdown/HTML解析错误
            if "parse" in error_text and ("entities" in error_text or "html" in error_text):
                logger.warning(f"格式解析错误，尝试无格式发送: {e}")
                try:
                    # 移除解析模式参数
                    if 'parse_mode' in kwargs:
                        kwargs_copy = kwargs.copy()
                        kwargs_copy.pop('parse_mode')
                        return await asyncio.wait_for(send_func(*args, **kwargs_copy), timeout=NET_TIMEOUT)
                except Exception as e2:
                    logger.error(f"无格式发送也失败: {e2}")
            
            # 处理网络相关错误
            elif any(kw in error_text for kw in ["network", "connection", "timeout"]):
                current_attempt += 1
                if current_attempt <= max_retries:
                    # 使用指数退避算法
                    delay = base_delay * (2 ** (current_attempt - 1))
                    logger.info(f"网络错误，将在 {delay} 秒后重试 ({current_attempt}/{max_retries}): {e}")
                    await asyncio.sleep(delay)
                    continue
            
            # 处理权限错误
            elif any(kw in error_text for kw in ["forbidden", "permission", "not enough rights", "blocked"]):
                logger.error(f"权限错误，无法发送消息: {e}")
                return None
            
            # 处理请求错误
            elif "bad request" in error_text:
                logger.error(f"无效请求错误: {e}")
                # 检查是否需要重试
                if "retry after" in error_text:
                    # 提取需要等待的秒数
                    import re
                    retry_seconds = 1
                    match = re.search(r"retry after (\d+)", error_text)
                    if match:
                        retry_seconds = int(match.group(1))
                    
                    logger.info(f"请求过于频繁，等待 {retry_seconds} 秒后重试")
                    await asyncio.sleep(retry_seconds)
                    continue
                return None
            
            # 其他错误
            else:
                logger.error(f"发送失败，未知错误: {e}")
            
            return None
    
    # 所有重试都失败
    logger.error(f"发送失败，已达到最大重试次数: {last_error}")
    return None

# 安全消息发送函数
async def send_message_safe(context, chat_id, text, **kwargs):
    """
    安全发送文本消息
    
    Args:
        context: 上下文对象
        chat_id: 聊天ID
        text: 消息文本
        kwargs: 其他参数
        
    Returns:
        发送的消息对象或None
    """
    return await enhanced_safe_send(context.bot.send_message, chat_id=chat_id, text=text, **kwargs)

async def reply_text_safe(message, text, **kwargs):
    """
    安全回复文本消息
    
    Args:
        message: 消息对象
        text: 回复文本
        kwargs: 其他参数
        
    Returns:
        回复的消息对象或None
    """
    return await enhanced_safe_send(message.reply_text, text=text, **kwargs)

async def send_media_group_safe(context, chat_id, media, **kwargs):
    """
    安全发送媒体组
    
    Args:
        context: 上下文对象
        chat_id: 聊天ID
        media: 媒体列表
        kwargs: 其他参数
        
    Returns:
        发送的媒体消息列表或None
    """
    return await enhanced_safe_send(context.bot.send_media_group, chat_id=chat_id, media=media, **kwargs)

async def edit_message_text_safe(context, chat_id, message_id, text, **kwargs):
    """
    安全编辑消息文本
    
    Args:
        context: 上下文对象
        chat_id: 聊天ID
        message_id: 消息ID
        text: 新文本
        kwargs: 其他参数
        
    Returns:
        编辑后的消息对象或None
    """
    return await enhanced_safe_send(
        context.bot.edit_message_text,
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        **kwargs
    )