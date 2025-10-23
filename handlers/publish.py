"""
投稿发布模块
"""
import json
import logging
import asyncio
from datetime import datetime
from telegram import (
    Update,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument
)
from telegram.ext import ConversationHandler, CallbackContext

from config.settings import CHANNEL_ID, NET_TIMEOUT, OWNER_ID, NOTIFY_OWNER
from database.db_manager import get_db, cleanup_old_data
from utils.helper_functions import build_caption, safe_send

logger = logging.getLogger(__name__)

async def save_published_post(user_id, message_id, data, media_list, doc_list):
    """
    保存已发布的帖子信息到数据库
    
    Args:
        user_id: 用户ID
        message_id: 频道消息ID
        data: 投稿数据
        media_list: 媒体列表
        doc_list: 文档列表
    """
    try:
        # 确定内容类型
        content_type = 'media' if media_list else 'document'
        if media_list and doc_list:
            content_type = 'mixed'
        
        # 获取文件ID列表
        file_ids = json.dumps(media_list if media_list else doc_list)
        
        # 提取标签（从tags字段）
        tags = data.get('tags', '')
        
        # 构建说明
        caption = build_caption(data)
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            await cursor.execute("""
                INSERT INTO published_posts 
                (message_id, user_id, username, title, tags, link, note,
                 content_type, file_ids, caption, publish_time, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id,
                user_id,
                data.get('username', f'user{user_id}'),
                data.get('title', ''),
                tags,
                data.get('link', ''),
                data.get('note', ''),
                content_type,
                file_ids,
                caption,
                datetime.now().timestamp(),
                datetime.now().timestamp()
            ))
            await conn.commit()
            logger.info(f"已保存帖子 {message_id} 到published_posts表")
    except Exception as e:
        logger.error(f"保存帖子信息到数据库失败: {e}")

async def publish_submission(update: Update, context: CallbackContext) -> int:
    """
    发布投稿到频道
    
    处理逻辑:
    1. 仅媒体模式: 将媒体发送到频道
    2. 仅文档模式或文档优先模式: 
       - 若同时有媒体和文档，则以媒体为主贴，文档组合作为回复
       - 若仅有文档，则以文档进行组合发送（说明文本放在最后一条）
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        
    Returns:
        int: 会话结束状态
    """
    user_id = update.effective_user.id
    try:
        async with get_db() as conn:
            c = await conn.cursor()
            await c.execute("SELECT * FROM submissions WHERE user_id=?", (user_id,))
            data = await c.fetchone()
        
        if not data:
            await update.message.reply_text("❌ 数据异常，请重新发送 /start")
            return ConversationHandler.END

        caption = build_caption(data)
        
        # 解析媒体和文档数据，增强型错误处理
        media_list = []
        doc_list = []
        
        try:
            if data["image_id"]:
                media_list = json.loads(data["image_id"])
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"解析媒体数据失败，user_id: {user_id}")
            media_list = []
            
        try:
            if data["document_id"]:
                doc_list = json.loads(data["document_id"])
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"解析文档数据失败，user_id: {user_id}")
            doc_list = []
        
        if not media_list and not doc_list:
            await update.message.reply_text("❌ 未检测到任何上传文件，请重新发送 /start")
            return ConversationHandler.END

        spoiler_flag = True if data["spoiler"].lower() == "true" else False
        sent_message = None
        
        # 处理媒体文件
        if media_list:
            sent_message = await handle_media_publish(context, media_list, caption, spoiler_flag)
        
        # 处理文档文件
        if doc_list:
            if sent_message:
                # 如果已经发送了媒体，则文档作为回复
                await handle_document_publish(
                    context, 
                    doc_list, 
                    None,  # 不需要重复发送说明，回复到主贴即可
                    sent_message.message_id
                )
            else:
                # 如果只有文档，直接发送
                sent_message = await handle_document_publish(context, doc_list, caption)
        
        # 处理结果
        if not sent_message:
            await update.message.reply_text("❌ 内容发送失败，请稍后再试")
            return ConversationHandler.END
            
        # 生成投稿链接
        if CHANNEL_ID.startswith('@'):
            channel_username = CHANNEL_ID.lstrip('@')
            submission_link = f"https://t.me/{channel_username}/{sent_message.message_id}"
        else:
            submission_link = "频道无公开链接"

        await update.message.reply_text(
            f"🎉 投稿已成功发布到频道！\n点击以下链接查看投稿：\n{submission_link}"
        )
        
        # 保存已发布的帖子信息到数据库（用于热度统计和搜索）
        await save_published_post(user_id, sent_message.message_id, data, media_list, doc_list)
        
        # 向所有者发送投稿通知
        if NOTIFY_OWNER and OWNER_ID:
            # 记录详细的调试信息
            logger.info(f"准备发送通知: NOTIFY_OWNER={NOTIFY_OWNER}, OWNER_ID={OWNER_ID}, 类型={type(OWNER_ID)}")
            
            # 获取用户名信息
            username = None
            try:
                username = data["username"] if "username" in data else f"user{user_id}"
            except (KeyError, TypeError):
                username = f"user{user_id}"
                
            # 获取用户名信息，优先使用真实用户名
            user = update.effective_user
            real_username = user.username or username
            
            # 安全处理可能缺失的数据字段
            try:
                mode = data["mode"] if "mode" in data else "未知"
                media_count = len(json.loads(data["image_id"])) if "image_id" in data and data["image_id"] else 0
                doc_count = len(json.loads(data["document_id"])) if "document_id" in data and data["document_id"] else 0
                tag_text = data["tag"] if "tag" in data else "无"
                title_text = data["title"] if "title" in data else "无"
                spoiler_text = "是" if "spoiler" in data and data["spoiler"] == "true" else "否"
            except Exception as e:
                logger.error(f"数据处理错误: {e}")
                # 设置默认值
                mode = "未知"
                media_count = 0
                doc_count = 0
                tag_text = "无"
                title_text = "无"
                spoiler_text = "否"
            
            # 构建纯文本通知消息（不使用任何Markdown，确保最大兼容性）
            notification_text = (
                f"📨 新投稿通知\n\n"
                f"👤 投稿人信息:\n"
                f"  • ID: {user_id}\n"
                f"  • 用户名: {('@' + real_username) if user.username else real_username}\n"
                f"  • 昵称: {user.first_name}{f' {user.last_name}' if user.last_name else ''}\n\n"
                
                f"🔗 查看投稿: {submission_link}\n\n"
                
                f"⚙️ 管理操作:\n"
                f"封禁此用户: /blacklist_add {user_id} 违规内容\n"
                f"查看黑名单: /blacklist_list"
            )
            
            try:
                # 确保OWNER_ID被转换为整数
                logger.info(f"尝试将OWNER_ID转换为整数: {OWNER_ID}")
                owner_id_int = int(OWNER_ID)
                logger.info(f"转换成功，准备发送通知到: {owner_id_int}")
                
                # 记录通知消息内容
                logger.info(f"通知消息长度: {len(notification_text)}, 使用纯文本格式")
                
                # 简化尝试逻辑 - 直接使用纯文本，不尝试任何格式化
                try:
                    message = await context.bot.send_message(
                        chat_id=owner_id_int,
                        text=notification_text
                    )
                    logger.info(f"通知发送成功！消息ID: {message.message_id}")
                except Exception as e:
                    logger.error(f"发送通知失败: {e}")
                    # 尝试使用更简化的消息
                    try:
                        simple_msg = f"📨 新投稿通知 - 用户 {real_username} (ID: {user_id}) 发布了新投稿\n链接: {submission_link}\n\n封禁命令: /blacklist_add {user_id} 违规内容"
                        await context.bot.send_message(
                            chat_id=owner_id_int,
                            text=simple_msg
                        )
                        logger.info("使用简化消息成功发送通知")
                    except Exception as e2:
                        logger.error(f"发送简化通知也失败: {e2}")
                        # 通知用户有问题
                        await update.message.reply_text(
                            "⚠️ 投稿已发布，但无法通知管理员。请直接联系管理员。"
                        )
            except ValueError as e:
                logger.error(f"OWNER_ID格式不正确，无法转换为整数: {OWNER_ID}, 错误: {e}")
                await update.message.reply_text(f"⚠️ 配置错误：OWNER_ID格式不正确。请联系开发者修复配置。")
            except Exception as e:
                logger.error(f"处理通知过程中发生其他错误: 错误类型: {type(e)}, 详细信息: {str(e)}")
                logger.error("异常追踪: ", exc_info=True)
        else:
            logger.info(f"不发送通知: NOTIFY_OWNER={NOTIFY_OWNER}, OWNER_ID={OWNER_ID}")
        
    except Exception as e:
        logger.error(f"发布投稿失败: {e}")
        await update.message.reply_text(f"❌ 发布失败，请联系管理员。错误信息：{str(e)}")
    finally:
        # 清理用户会话数据
        try:
            async with get_db() as conn:
                c = await conn.cursor()
                await c.execute("DELETE FROM submissions WHERE user_id=?", (user_id,))
            logger.info(f"已删除用户 {user_id} 的投稿记录")
        except Exception as e:
            logger.error(f"删除数据错误: {e}")
        
        # 清理过期数据
        await cleanup_old_data()
    
    return ConversationHandler.END

async def handle_media_publish(context, media_list, caption, spoiler_flag):
    """
    处理媒体发布
    
    Args:
        context: 回调上下文
        media_list: 媒体列表
        caption: 说明文本
        spoiler_flag: 是否剧透标志
        
    Returns:
        发送的消息对象或None
    """
    # 检查caption长度，如果过长先单独发送
    caption_message = None
    
    # 强制检查caption长度，保证媒体组发送的可靠性
    # 不管SHOW_SUBMITTER如何设置，当caption超过850字符时都单独发送
    # 使用较小的阈值（850而不是1000）来确保足够的安全边际
    if caption and len(caption) > 850:
        logger.info(f"Caption过长 ({len(caption)} 字符)，单独发送caption")
        try:
            caption_message = await safe_send(
                context.bot.send_message,
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode='HTML'
            )
            # 媒体组将不再包含caption
            caption = None
        except Exception as e:
            logger.error(f"发送长caption失败: {e}")
            # 继续尝试发送媒体，但不带caption

    # 单个媒体处理
    if len(media_list) == 1:
        typ, file_id = media_list[0].split(":", 1)
        try:
            # 如果已经单独发送了caption，则不再添加到媒体
            media_caption = None if caption_message else caption
            
            if typ == "photo":
                sent_message = await safe_send(
                    context.bot.send_photo,
                    chat_id=CHANNEL_ID,
                    photo=file_id,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None,
                    has_spoiler=spoiler_flag,
                    reply_to_message_id=caption_message.message_id if caption_message else None
                )
            elif typ == "video":
                sent_message = await safe_send(
                    context.bot.send_video,
                    chat_id=CHANNEL_ID,
                    video=file_id,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None,
                    has_spoiler=spoiler_flag,
                    reply_to_message_id=caption_message.message_id if caption_message else None
                )
            elif typ == "animation":
                sent_message = await safe_send(
                    context.bot.send_animation,
                    chat_id=CHANNEL_ID,
                    animation=file_id,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None,
                    has_spoiler=spoiler_flag,
                    reply_to_message_id=caption_message.message_id if caption_message else None
                )
            elif typ == "audio":
                sent_message = await safe_send(
                    context.bot.send_audio,
                    chat_id=CHANNEL_ID,
                    audio=file_id,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None,
                    reply_to_message_id=caption_message.message_id if caption_message else None
                )
            
            return caption_message or sent_message
        except Exception as e:
            logger.error(f"发送单条媒体失败: {e}")
            return caption_message  # 如果至少发送了caption消息，则返回它
    
    # 多个媒体处理 - 将媒体分组，每组最多10个
    else:
        try:
            all_sent_messages = []
            success_groups = 0
            total_groups = (len(media_list) + 9) // 10  # 向上取整计算总组数
            first_message = caption_message  # 如果单独发送了caption，用它作为第一条消息
            
            # 将媒体列表分成每组最多10个项目
            for chunk_index in range(0, len(media_list), 10):
                media_chunk = media_list[chunk_index:chunk_index + 10]
                media_group = []
                
                group_number = chunk_index // 10 + 1
                logger.info(f"处理第{group_number}组媒体，共{len(media_chunk)}个项目 (总共{total_groups}组)")
                
                for i, m in enumerate(media_chunk):
                    typ, file_id = m.split(":", 1)
                    # 只在第一组的第一个媒体添加说明（如果caption不为None且没有单独发送）
                    # 强制设置简短的caption，即使SHOW_SUBMITTER=True也能可靠发送
                    use_caption = caption if (chunk_index == 0 and i == 0 and caption is not None and not caption_message) else None
                    use_parse_mode = 'HTML' if use_caption else None
                    
                    if typ == "photo":
                        media_group.append(InputMediaPhoto(
                            media=file_id,
                            caption=use_caption,
                            parse_mode=use_parse_mode,
                            has_spoiler=spoiler_flag
                        ))
                    elif typ == "video":
                        media_group.append(InputMediaVideo(
                            media=file_id,
                            caption=use_caption,
                            parse_mode=use_parse_mode,
                            has_spoiler=spoiler_flag
                        ))
                    elif typ == "animation":
                        media_group.append(InputMediaAnimation(
                            media=file_id,
                            caption=use_caption,
                            parse_mode=use_parse_mode,
                            has_spoiler=spoiler_flag
                        ))
                    elif typ == "audio":
                        media_group.append(InputMediaAudio(
                            media=file_id,
                            caption=use_caption,
                            parse_mode=use_parse_mode
                        ))
                
                # 发送当前组，增加超时参数
                extended_timeout = 60  # 更长的超时时间，避免误判为超时
                if first_message is None:
                    logger.info(f"发送第{group_number}组媒体（首组），{len(media_group)}个媒体项目")
                    # 第一组直接发送
                    try:
                        sent_messages = await asyncio.wait_for(
                            context.bot.send_media_group(
                                chat_id=CHANNEL_ID,
                                media=media_group
                            ),
                            timeout=extended_timeout
                        )
                        
                        if sent_messages and len(sent_messages) > 0:
                            all_sent_messages.extend(sent_messages)
                            first_message = sent_messages[0]  # 保存第一条消息，用于回复
                            logger.info(f"第{group_number}组媒体发送成功，message_id={first_message.message_id}")
                            success_groups += 1
                        else:
                            logger.error(f"第{group_number}组媒体发送返回空结果")
                    except asyncio.TimeoutError:
                        logger.warning(f"第{group_number}组媒体发送超时，但可能已成功发送")
                        # 即使超时，尝试继续后续组的发送
                        # 等待3秒，让Telegram服务器有时间处理
                        await asyncio.sleep(3)
                    except Exception as e:
                        logger.error(f"第{group_number}组媒体发送失败: {e}")
                        
                        # 如果是网络相关错误，休眠更长时间后继续
                        if any(keyword in str(e).lower() for keyword in ["network", "connection", "timeout"]):
                            await asyncio.sleep(5)
                else:
                    logger.info(f"发送第{group_number}组媒体（回复组），{len(media_group)}个媒体项目，回复到message_id={first_message.message_id}")
                    # 后续组作为回复发送到第一条消息
                    try:
                        sent_messages = await asyncio.wait_for(
                            context.bot.send_media_group(
                                chat_id=CHANNEL_ID,
                                media=media_group,
                                reply_to_message_id=first_message.message_id
                            ),
                            timeout=extended_timeout
                        )
                        
                        if sent_messages and len(sent_messages) > 0:
                            all_sent_messages.extend(sent_messages)
                            logger.info(f"第{group_number}组媒体发送成功，第一条message_id={sent_messages[0].message_id}")
                            success_groups += 1
                        else:
                            logger.error(f"第{group_number}组媒体发送返回空结果")
                    except asyncio.TimeoutError:
                        logger.warning(f"第{group_number}组媒体发送超时，但可能已成功发送")
                        # 即使超时，尝试继续后续组的发送
                        # 等待3秒，让Telegram服务器有时间处理
                        await asyncio.sleep(3)
                    except Exception as e:
                        logger.error(f"第{group_number}组媒体发送失败: {e}")
                        
                        # 如果是网络相关错误，休眠更长时间后继续
                        if any(keyword in str(e).lower() for keyword in ["network", "connection", "timeout"]):
                            await asyncio.sleep(5)
                
                # 添加更长的延迟，避免API限制
                # 每组之间等待2秒，给Telegram API更多处理时间
                await asyncio.sleep(2)
            
            # 计算实际处理的媒体数量并记录结果
            total_media_estimate = success_groups * 10
            if success_groups < total_groups and len(all_sent_messages) == 0:
                logger.warning(f"媒体发送部分超时，预计已发送约{total_media_estimate}个媒体项目（可能不准确）")
            else:
                logger.info(f"所有媒体发送完成，{success_groups}/{total_groups}组成功，共{len(all_sent_messages)}个媒体项目成功记录")
            
            # 返回第一条消息或任何成功发送的消息
            return first_message if first_message else (all_sent_messages[0] if all_sent_messages else None)
        except Exception as e:
            logger.error(f"发送媒体组失败: {e}")
            return caption_message  # 如果至少发送了caption消息，则返回它

async def handle_document_publish(context, doc_list, caption=None, reply_to_message_id=None):
    """
    处理文档发布
    
    Args:
        context: 回调上下文
        doc_list: 文档列表
        caption: 说明文本，如果为None则不添加说明
        reply_to_message_id: 回复的消息ID，如果为None则创建新消息
        
    Returns:
        发送的消息对象或None
    """
    if len(doc_list) == 1 and caption is not None:
        # 单个文档处理
        _, file_id = doc_list[0].split(":", 1)
        try:
            return await safe_send(
                context.bot.send_document,
                chat_id=CHANNEL_ID,
                document=file_id,
                caption=caption,
                parse_mode='HTML',
                reply_to_message_id=reply_to_message_id
            )
        except Exception as e:
            logger.error(f"发送单个文档失败: {e}")
            return None
    else:
        # 多个文档处理，使用文档组
        try:
            doc_media_group = []
            for i, doc_item in enumerate(doc_list):
                _, file_id = doc_item.split(":", 1)
                # 只在最后一个文档添加说明，且caption不为None
                caption_to_use = caption if (i == len(doc_list) - 1 and caption is not None) else None
                doc_media_group.append(InputMediaDocument(
                    media=file_id,
                    caption=caption_to_use,
                    parse_mode='HTML' if caption_to_use else None
                ))
            
            sent_docs = await safe_send(
                context.bot.send_media_group,
                chat_id=CHANNEL_ID,
                media=doc_media_group,
                reply_to_message_id=reply_to_message_id
            )
            
            if sent_docs and len(sent_docs) > 0:
                return sent_docs[0]
            return None
        except Exception as e:
            logger.error(f"发送文档组失败: {e}")
            return None