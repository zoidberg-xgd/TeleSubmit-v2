"""
文档处理模块
"""
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from models.state import STATE
from database.db_manager import get_db
from utils.helper_functions import validate_state
from utils.file_validator import create_file_validator
from config.settings import ALLOWED_FILE_TYPES

logger = logging.getLogger(__name__)

# 创建全局文件类型验证器
file_validator = create_file_validator(ALLOWED_FILE_TYPES)

@validate_state(STATE['DOC'])
async def handle_doc(update: Update, context: CallbackContext) -> int:
    """
    处理文档文件上传
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        
    Returns:
        int: 当前会话状态
    """
    logger.info(f"处理文档输入，user_id: {update.effective_user.id}")
    user_id = update.effective_user.id
    
    if not update.message.document:
        logger.warning(f"收到非文档消息，但被路由到文档处理，user_id: {user_id}")
        
        # 获取允许的文件类型描述
        allowed_types_desc = file_validator.get_allowed_types_description()
        
        await update.message.reply_text(
            f"⚠️ 请发送文档文件\n\n"
            f"📎 请以文件附件形式发送：\n"
            f"• 点击聊天输入框旁的📎图标\n"
            f"• 选择文件或文档\n\n"
            f"✅ 允许的文件类型：\n{allowed_types_desc}"
        )
        return STATE['DOC']
    
    doc = update.message.document
    
    # 验证文件类型
    is_valid, error_msg = file_validator.validate(doc.file_name, doc.mime_type)
    if not is_valid:
        logger.warning(f"文件类型验证失败: user_id={user_id}, file={doc.file_name}, mime={doc.mime_type}")
        await update.message.reply_text(error_msg)
        return STATE['DOC']
    
    logger.info(f"文件类型验证通过: user_id={user_id}, file={doc.file_name}, mime={doc.mime_type}")
    # 存储格式：document:file_id:filename
    filename = doc.file_name or "未命名文件"
    new_doc = f"document:{doc.file_id}:{filename}"
    
    try:
        async with get_db() as conn:
            c = await conn.cursor()
            await c.execute("SELECT document_id FROM submissions WHERE user_id=?", (user_id,))
            row = await c.fetchone()
            
            if not row:
                await update.message.reply_text("❌ 会话已过期，请重新发送 /start")
                return ConversationHandler.END
                
            # 增强型错误处理
            doc_list = []
            try:
                if row["document_id"]:
                    doc_list = json.loads(row["document_id"])
            except (json.JSONDecodeError, TypeError):
                doc_list = []
            
            # 限制文档数量为10个
            if len(doc_list) >= 10:
                await update.message.reply_text("⚠️ 已达到文档上传上限（10个）")
                return STATE['DOC']
                
            doc_list.append(new_doc)
            await c.execute("UPDATE submissions SET document_id=?, timestamp=? WHERE user_id=?",
                      (json.dumps(doc_list), datetime.now().timestamp(), user_id))
        
        logger.info(f"当前文档数量：{len(doc_list)}")
        await update.message.reply_text(
            f"✅ 已接收文档，共计 {len(doc_list)} 个。\n继续发送文档文件，或发送 /done_doc 完成上传。"
        )
    except Exception as e:
        logger.error(f"文档保存错误: {e}")
        await update.message.reply_text("❌ 文档保存失败，请稍后再试")
        return ConversationHandler.END
        
    return STATE['DOC']

@validate_state(STATE['DOC'])
async def done_doc(update: Update, context: CallbackContext) -> int:
    """
    完成文档上传，进入下一阶段
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        
    Returns:
        int: 下一个会话状态
    """
    logger.info(f"文档上传结束，user_id: {update.effective_user.id}")
    user_id = update.effective_user.id
    
    try:
        async with get_db() as conn:
            c = await conn.cursor()
            await c.execute("SELECT document_id, mode FROM submissions WHERE user_id=?", (user_id,))
            row = await c.fetchone()
            
            if not row:
                await update.message.reply_text("❌ 会话已过期，请重新发送 /start")
                return ConversationHandler.END
                
            # 增强型错误处理
            doc_list = []
            try:
                if row["document_id"]:
                    doc_list = json.loads(row["document_id"])
            except (json.JSONDecodeError, TypeError):
                doc_list = []
            
            # 文档必选 - 检查至少有一个文档
            if not doc_list:
                await update.message.reply_text(
                    "⚠️ 请至少发送一个文档文件\n\n"
                    "📎 请以文件附件形式发送：\n"
                    "• 点击聊天输入框旁的📎图标\n"
                    "• 选择文件或文档\n"
                    "• 支持ZIP、RAR等压缩包以及PDF、DOC等各种文档格式"
                )
                return STATE['DOC']
                
            # 判断模式，决定下一步流程
            mode = row["mode"] if "mode" in row.keys() else "mixed"
            mode = mode.lower() if mode else "mixed"
            
            # 不论什么模式，完成文档上传后都进入媒体上传阶段
            await update.message.reply_text(
                "✅ 文档接收完成。\n现在请发送媒体文件（可选）：\n\n"
                "📱 支持的媒体格式：\n"
                "• 图片：直接从相册选择发送\n"
                "• 视频：直接发送视频（非文件形式）\n"
                "• GIF：直接发送GIF动图\n"
                "• 音频：直接发送语音或音频\n\n"
                "最多上传10个文件。\n"
                "发送完毕后，请发送 /done_media，或发送 /skip_media 跳过媒体上传步骤。"
            )
            return STATE['MEDIA']
    except Exception as e:
        logger.error(f"检索文档错误: {e}")
        await update.message.reply_text("❌ 内部错误，请稍后再试")
        return ConversationHandler.END

async def prompt_doc(update: Update, context: CallbackContext) -> int:
    """
    提示用户发送文档文件
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        
    Returns:
        int: 当前会话状态
    """
    # 获取允许的文件类型描述
    allowed_types_desc = file_validator.get_allowed_types_description()
    
    await update.message.reply_text(
        f"请发送文档文件，或发送 /done_doc 完成上传\n\n"
        f"📎 请以文件附件形式发送：\n"
        f"• 点击聊天输入框旁的📎图标\n"
        f"• 选择文件或文档\n\n"
        f"✅ 允许的文件类型：\n{allowed_types_desc}"
    )
    return STATE['DOC']