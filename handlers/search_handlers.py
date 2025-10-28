"""
帖子搜索和标签管理模块
"""
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from whoosh.query import DateRange

from config.settings import CHANNEL_ID, OWNER_ID
from database.db_manager import get_db
from utils.search_engine import get_search_engine
from utils.cache import TTLCache

logger = logging.getLogger(__name__)

# 简单缓存：标签云 60s
_tag_cloud_cache = TTLCache(default_ttl=60, max_size=16)


def is_owner(user_id: int) -> bool:
    """检查用户是否是 OWNER"""
    return OWNER_ID and user_id == OWNER_ID


async def search_posts(update: Update, context: CallbackContext):
    """
    搜索已发布的帖子 - 使用全文搜索引擎（支持中文分词）
    
    命令格式：
    /search <关键词> [选项]
    
    搜索范围：标题、描述、标签
    
    示例：
    /search Python - 搜索包含 Python 的帖子
    /search #编程 - 搜索带有"编程"标签的帖子
    /search Python -t week - 搜索本周包含 Python 的帖子
    
    选项：
    -t day/week/month - 时间范围过滤
    -n <数量> - 限制结果数量（默认10，最多30）
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    user_id = update.effective_user.id
    
    try:
        # 解析参数
        if not context.args:
            await update.message.reply_text(
                "🔍 搜索帮助\n\n"
                "使用方法：\n"
                "/search <关键词> [选项]\n\n"
                "示例：\n"
                "• /search Python\n"
                "• /search #编程\n"
                "• /search 教程 -t week\n"
                "• /search API -n 20\n"
                "• /search 文件名.txt\n\n"
                "搜索范围：\n"
                "• 标题、简介、标签、文件名\n\n"
                "选项：\n"
                "• -t day/week/month - 时间范围\n"
                "• -n <数量> - 结果数量（最多30）\n\n"
                "💡 使用 /tags 查看所有标签\n"
                "✨ 支持中文分词和文件名搜索！"
            )
            return
        
        # 解析搜索参数
        args = context.args
        keyword = None
        time_filter_str = None
        limit = 10
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == '-t' and i + 1 < len(args):
                # 时间过滤选项
                time_filter_str = args[i + 1].lower()
                i += 2
            elif arg == '-n' and i + 1 < len(args):
                # 数量限制选项
                try:
                    limit = min(int(args[i + 1]), 30)
                except ValueError:
                    limit = 10
                i += 2
            else:
                # 关键词
                if keyword is None:
                    keyword = arg
                else:
                    keyword += ' ' + arg
                i += 1
        
        if not keyword:
            await update.message.reply_text("❌ 请提供搜索关键词")
            return
        
        # 检查是否是标签搜索
        is_tag_search = keyword.startswith('#')
        tag_filter = None
        if is_tag_search:
            tag_filter = keyword.lstrip('#')
            keyword = tag_filter  # 也搜索关键词
        
        # 构建时间过滤器
        time_filter = None
        time_desc = ""
        
        if time_filter_str == 'day':
            start_time = datetime.now() - timedelta(days=1)
            time_filter = DateRange("publish_time", start_time, None)
            time_desc = "今日"
        elif time_filter_str == 'week':
            start_time = datetime.now() - timedelta(days=7)
            time_filter = DateRange("publish_time", start_time, None)
            time_desc = "本周"
        elif time_filter_str == 'month':
            start_time = datetime.now() - timedelta(days=30)
            time_filter = DateRange("publish_time", start_time, None)
            time_desc = "本月"
        
        # 处理时间过滤（来自内联时间筛选）
        time_filter = context.user_data.get('time_filter')
        if time_filter:
            # 将时间过滤转换为 -t 选项处理逻辑
            if '-t' not in context.args:
                context.args.extend(['-t', time_filter])
            context.user_data['time_filter'] = None

        # 使用搜索引擎
        search_engine = get_search_engine()
        
        # 执行搜索
        search_result = search_engine.search(
            query_str=keyword,
            page_num=1,
            page_len=limit,
            time_filter=time_filter,
            tag_filter=tag_filter if is_tag_search else None,
            sort_by="publish_time"
        )
        
        if not search_result.hits:
            search_desc = f"标签 #{tag_filter}" if is_tag_search else f"关键词 \"{keyword}\""
            await update.message.reply_text(
                f"🔍 未找到匹配{time_desc}{search_desc}的帖子"
            )
            return
        
        # 构建结果消息
        search_desc = f"#{tag_filter}" if is_tag_search else f"\"{keyword}\""
        time_prefix = f"{time_desc} " if time_desc else ""
        message = f"🔍 搜索结果：{time_prefix}{search_desc}\n"
        message += f"找到 {search_result.total_results} 个结果（显示前 {len(search_result.hits)} 个）\n\n"
        
        # 存储消息ID用于删除按钮
        message_ids = []
        
        for idx, hit in enumerate(search_result.hits, 1):
            # 生成帖子链接
            if CHANNEL_ID.startswith('@'):
                channel_username = CHANNEL_ID.lstrip('@')
                post_link = f"https://t.me/{channel_username}/{hit.message_id}"
            else:
                post_link = f"消息ID: {hit.message_id}"
            
            # 解析标签
            try:
                tags = json.loads(hit.tags) if hit.tags else []
                tags_preview = ' '.join([f"#{tag}" for tag in tags[:3]])
            except (json.JSONDecodeError, TypeError, AttributeError):
                tags_preview = hit.tags[:50] if hit.tags else ""
            
            # 使用高亮标题（如果有）
            title = hit.highlighted_title or hit.title or '无标题'
            # 清理HTML标签用于长度计算
            import re
            title_clean = re.sub(r'<[^>]+>', '', title)
            
            # 标题过长则截断
            if len(title_clean) > 40:
                title = title[:60] + '...'  # 考虑HTML标签，使用更大的截断长度
            
            # 发布时间
            publish_date = hit.publish_time.strftime('%Y-%m-%d')
            
            # 匹配字段提示
            matched_info = ""
            if hasattr(hit, 'matched_fields') and hit.matched_fields:
                matched_info = f"   💡 匹配: {', '.join(hit.matched_fields)}\n"
            
            message += (
                f"{idx}. {title}\n"
                f"   {tags_preview}\n"
                f"{matched_info}"
                f"   📅 {publish_date} | 👀 {hit.views} | 🔥 {hit.heat_score:.0f}\n"
                f"   🔗 {post_link}\n\n"
            )
            
            # 存储message_id供删除功能使用
            if hit.message_id:
                message_ids.append((idx, hit.message_id))
            
            # 防止消息过长
            if len(message) > 3500:
                message += "...\n\n结果过多，请使用更具体的关键词"
                break
        
        # 如果是 OWNER，添加删除按钮
        if is_owner(user_id) and message_ids:
            keyboard = []
            # 每行最多3个按钮
            row = []
            for idx, msg_id in message_ids[:9]:  # 最多显示9个按钮（3x3）
                row.append(InlineKeyboardButton(f"🗑️ {idx}", callback_data=f"delete_post_{msg_id}"))
                if len(row) == 3:
                    keyboard.append(row)
                    row = []
            if row:  # 添加剩余的按钮
                keyboard.append(row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                message, 
                disable_web_page_preview=True, 
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(message, disable_web_page_preview=True, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"搜索帖子失败: {e}", exc_info=True)
        await update.message.reply_text("❌ 搜索失败，请稍后重试")


async def handle_search_input(update: Update, context: CallbackContext):
    """在选择了搜索模式后，接收用户输入的关键词/标签并执行搜索。"""
    mode = context.user_data.get('search_mode')
    if not mode:
        return  # 未处于搜索输入模式，交给其他处理器
    text = (update.message.text or '').strip()
    if not text:
        await update.message.reply_text("❌ 请输入搜索关键词")
        return
    # 提前给用户反馈，避免首次加载分词器带来的感知延迟
    try:
        await update.message.reply_text("⏳ 正在搜索…")
    except Exception:
        pass
    # 将文本转换为 /search 的参数形式并复用 search_posts 逻辑
    if mode == 'tag' and not text.startswith('#'):
        text = f"#{text}"
    try:
        # 设置上下文参数并调用已有的搜索逻辑
        context.args = [text]
        await search_posts(update, context)
    finally:
        # 退出搜索输入模式
        context.user_data['search_mode'] = None


async def search_posts_by_tag(update: Update, context: CallbackContext, tag: str = None):
    """
    按标签搜索帖子（回调查询专用）
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
        tag: 要搜索的标签
    """
    # 如果没有提供标签，从context.args获取
    if tag is None:
        if not context.args:
            await update.message.reply_text("❌ 请提供要搜索的标签")
            return
        tag = context.args[0]
    
    # 移除标签前面的#号（如果有）并转换为小写
    tag = tag.lstrip('#').lower()
    
    try:
        # 使用搜索引擎
        search_engine = get_search_engine()
        
        # 执行标签搜索
        search_result = search_engine.search(
            query_str=tag,  # 关键词也搜索标签内容
            page_num=1,
            page_len=10,
            tag_filter=tag,  # 使用标签过滤
            sort_by="publish_time"
        )
        
        if not search_result.hits:
            # 根据update类型选择回复方式
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(f"🔍 未找到标签 #{tag} 的帖子")
            else:
                await update.message.reply_text(f"🔍 未找到标签 #{tag} 的帖子")
            return
        
        # 构建结果消息
        message = f"🏷️ 标签搜索结果：#{tag}\n"
        message += f"找到 {search_result.total_results} 个结果（显示前 {len(search_result.hits)} 个）\n\n"
        
        for idx, hit in enumerate(search_result.hits, 1):
            # 生成帖子链接
            if CHANNEL_ID.startswith('@'):
                channel_username = CHANNEL_ID.lstrip('@')
                post_link = f"https://t.me/{channel_username}/{hit.message_id}"
            else:
                post_link = f"消息ID: {hit.message_id}"
            
            title = hit.title or '无标题'
            if len(title) > 40:
                title = title[:37] + '...'
            
            # 发布时间
            publish_date = hit.publish_time.strftime('%Y-%m-%d')
            
            message += (
                f"{idx}. {title}\n"
                f"   📅 {publish_date} | 👀 {hit.views} | 🔥 {hit.heat_score:.0f}\n"
                f"   🔗 {post_link}\n\n"
            )
            
            # 防止消息过长
            if len(message) > 3500:
                message += "...\n\n结果过多，请使用更具体的关键词"
                break
        
        # 根据update类型选择回复方式
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text(message, disable_web_page_preview=True)
        else:
            await update.message.reply_text(message, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"按标签搜索失败: {e}", exc_info=True)
        # 根据update类型选择回复方式
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text("❌ 搜索失败，请稍后重试")
        else:
            await update.message.reply_text("❌ 搜索失败，请稍后重试")


async def get_tag_cloud(update: Update, context: CallbackContext):
    """
    获取标签云（显示所有标签及其使用次数）
    
    命令格式：
    /tags [数量]
    
    示例：
    /tags - 显示前20个热门标签
    /tags 50 - 显示前50个热门标签
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    try:
        # 解析参数
        limit = 20
        if context.args and context.args[0].isdigit():
            limit = min(int(context.args[0]), 100)
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            # 获取所有帖子的标签
            await cursor.execute("SELECT tags FROM published_posts WHERE tags IS NOT NULL")
            posts = await cursor.fetchall()
        
        if not posts:
            await update.message.reply_text("📊 暂无标签数据")
            return
        
        # 统计标签使用次数
        tag_counts = {}
        for post in posts:
            try:
                # 尝试作为 JSON 解析（兼容旧数据）
                tags = json.loads(post['tags'])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            except (json.JSONDecodeError, TypeError, ValueError):
                # 如果不是 JSON，按空格分割（当前格式：'#测试 #标签2'）
                tags_text = post['tags']
                if tags_text:
                    tags = tags_text.split()
                    for tag in tags:
                        # 移除 # 前缀，统一处理
                        tag_clean = tag.lstrip('#')
                        if tag_clean:
                            tag_counts[tag_clean] = tag_counts.get(tag_clean, 0) + 1
        
        if not tag_counts:
            await update.message.reply_text("📊 暂无标签数据")
            return
        
        # 按使用次数排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # 缓存命中（按 limit 区分）
        cache_key = f"tag_cloud:{limit}"
        cached = _tag_cloud_cache.get(cache_key)
        if cached:
            await update.message.reply_text(cached)
            return

        # 构建标签云消息
        message = f"🏷️ 标签云 TOP {len(sorted_tags)}\n\n"
        
        for idx, (tag, count) in enumerate(sorted_tags, 1):
            # 使用不同的表情符号表示热度
            if idx <= 3:
                emoji = "🔥"
            elif idx <= 10:
                emoji = "⭐"
            else:
                emoji = "📌"
            
            message += f"{emoji} #{tag} ({count})\n"
            
            # 每10个标签换一次行，使排版更美观
            if idx % 10 == 0 and idx < len(sorted_tags):
                message += "\n"
        
        message += f"\n💡 使用 /search #{sorted_tags[0][0]} 搜索该标签的帖子"
        
        _tag_cloud_cache.set(cache_key, message, ttl=60)
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"获取标签云失败: {e}")
        await update.message.reply_text("❌ 获取标签云失败，请稍后重试")


async def get_my_posts(update: Update, context: CallbackContext):
    """
    查看自己发布的所有帖子
    
    命令格式：
    /myposts [数量]
    
    示例：
    /myposts - 查看最近10篇投稿
    /myposts 20 - 查看最近20篇投稿
    
    注意：
    - 普通用户只能查看自己的投稿列表
    - OWNER 可以看到删除按钮来管理帖子
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    from config.settings import OWNER_ID
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    user_id = update.effective_user.id
    is_owner = (user_id == OWNER_ID)
    
    try:
        # 支持从消息或回调两种入口回复
        reply_target = update.message if getattr(update, 'message', None) else (
            update.callback_query.message if getattr(update, 'callback_query', None) else None
        )
        # 解析参数
        limit = 10
        if context.args and context.args[0].isdigit():
            limit = min(int(context.args[0]), 50)
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            # 获取用户的帖子
            await cursor.execute(
                "SELECT * FROM published_posts WHERE user_id = ? ORDER BY publish_time DESC LIMIT ?",
                (user_id, limit)
            )
            user_posts = await cursor.fetchall()
        
        if not user_posts:
            await reply_target.reply_text(
                "📝 您还没有发布过投稿\n\n"
                "使用 /submit 开始创建您的第一篇投稿！"
            )
            return
        
        # 逐条发送帖子，每个帖子带操作按钮
        await reply_target.reply_text(
            f"📝 我的投稿（最近 {len(user_posts)} 篇）\n\n"
            f"{'💡 提示：作为管理员，您可以直接删除帖子' if is_owner else '💡 提示：点击按钮查看帖子详情'}"
        )
        
        for idx, post in enumerate(user_posts, 1):
            # 生成帖子链接
            if CHANNEL_ID.startswith('@'):
                channel_username = CHANNEL_ID.lstrip('@')
                post_link = f"https://t.me/{channel_username}/{post['message_id']}"
            else:
                post_link = f"消息ID: {post['message_id']}"
            
            # 解析标签
            try:
                tags = json.loads(post['tags']) if post['tags'] else []
                tags_preview = ' '.join([f"#{tag}" for tag in tags[:3]])
            except (json.JSONDecodeError, TypeError, KeyError):
                tags_preview = ""
            
            title = post['title'] or '无标题'
            # 标题过长则截断
            if len(title) > 40:
                title = title[:37] + '...'
            
            # 发布时间
            publish_date = datetime.fromtimestamp(post['publish_time']).strftime('%Y-%m-%d %H:%M')
            
            message = (
                f"📄 {idx}. {title}\n"
                f"{tags_preview}\n"
                f"📅 {publish_date}\n"
                f"📊 浏览 {post['views']} | 转发 {post['forwards']} | 热度 {post['heat_score']:.0f}\n"
                f"🔗 {post_link}"
            )
            
            # 构建内联键盘
            keyboard = []
            
            # 第一行：查看帖子按钮
            row1 = [InlineKeyboardButton("👁️ 查看原帖", url=post_link)]
            keyboard.append(row1)
            
            # 第二行：仅 OWNER 可见的删除按钮
            if is_owner and post['message_id']:
                row2 = [
                    InlineKeyboardButton("🗑️ 删除", callback_data=f"delete_post_{post['message_id']}")
                ]
                keyboard.append(row2)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # 发送单个帖子信息
            await reply_target.reply_text(
                message,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            # 防止消息过多，最多显示前20篇
            if idx >= 20:
                await reply_target.reply_text(
                    f"...\n\n还有更多投稿，使用 /myposts {limit + 10} 查看更多"
                )
                break
        
        # 最后发送统计提示
        await reply_target.reply_text("💡 使用 /mystats 查看完整统计")
        
    except Exception as e:
        logger.error(f"获取用户帖子失败: {e}", exc_info=True)
        try:
            await reply_target.reply_text("❌ 获取帖子列表失败，请稍后重试")
        except Exception:
            pass


async def search_by_user(update: Update, context: CallbackContext):
    """
    按用户ID搜索帖子（管理员功能）
    
    命令格式：
    /searchuser <user_id>
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    from config.settings import OWNER_ID
    from utils.blacklist import is_owner
    
    # 仅管理员可用（使用is_owner函数确保正确比较）
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ 此命令仅管理员可用")
        return
    
    try:
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text(
                "使用方法：\n/searchuser <user_id>\n\n"
                "示例：/searchuser 123456789"
            )
            return
        
        target_user_id = int(context.args[0])
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            # 获取指定用户的所有帖子
            await cursor.execute(
                "SELECT * FROM published_posts WHERE user_id = ? ORDER BY publish_time DESC",
                (target_user_id,)
            )
            user_posts = await cursor.fetchall()
        
        if not user_posts:
            await update.message.reply_text(f"🔍 用户 {target_user_id} 没有发布过帖子")
            return
        
        # 统计数据
        total_posts = len(user_posts)
        total_views = sum(post['views'] for post in user_posts)
        total_forwards = sum(post['forwards'] for post in user_posts)
        
        message = (
            f"👤 用户 {target_user_id} 的投稿\n\n"
            f"📊 统计：\n"
            f"• 总投稿：{total_posts}\n"
            f"• 总浏览：{total_views}\n"
            f"• 总转发：{total_forwards}\n\n"
            f"最近投稿：\n\n"
        )
        
        # 显示最近10篇
        for idx, post in enumerate(user_posts[:10], 1):
            if CHANNEL_ID.startswith('@'):
                channel_username = CHANNEL_ID.lstrip('@')
                post_link = f"https://t.me/{channel_username}/{post['message_id']}"
            else:
                post_link = f"消息ID: {post['message_id']}"
            
            title = post['title'] or '无标题'
            if len(title) > 30:
                title = title[:27] + '...'
            
            publish_date = datetime.fromtimestamp(post['publish_time']).strftime('%Y-%m-%d')
            
            message += (
                f"{idx}. {title}\n"
                f"   📅 {publish_date} | 👀 {post['views']}\n"
                f"   🔗 {post_link}\n\n"
            )
        
        if len(user_posts) > 10:
            message += f"... 还有 {len(user_posts) - 10} 篇投稿"
        
        await update.message.reply_text(message, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"按用户搜索失败: {e}")
        await update.message.reply_text("❌ 搜索失败，请稍后重试")


async def delete_posts_batch(update: Update, context: CallbackContext):
    """
    批量删除帖子（仅 OWNER 可用）
    
    命令格式：
    /delete_posts [message_id1] [message_id2] ... [message_idN]
    或
    /delete_posts [message_id1-message_id2]  (删除连续范围)
    
    示例：
    /delete_posts 123 456 789 - 删除消息ID为 123、456、789 的帖子
    /delete_posts 100-110 - 删除消息ID从 100 到 110 的所有帖子
    /delete_posts 100-110 150 200-205 - 混合使用范围和单个ID
    
    注意：
    - 仅限 OWNER 使用
    - 只删除数据库记录和搜索索引，不删除频道消息
    - 一次最多删除 50 个帖子
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    from config.settings import OWNER_ID
    from utils.blacklist import is_owner
    
    user_id = update.effective_user.id
    
    # 检查权限：只有 OWNER 可以批量删除
    if not is_owner(user_id):
        await update.message.reply_text("⛔ 权限不足：只有管理员可以批量删除帖子")
        logger.warning(f"用户 {user_id} 尝试批量删除但权限不足")
        return
    
    # 检查参数
    if not context.args:
        await update.message.reply_text(
            "📝 <b>批量删除帮助</b>\n\n"
            "<b>命令格式：</b>\n"
            "<code>/delete_posts [message_id1] [message_id2] ...</code>\n"
            "<code>/delete_posts [start_id-end_id]</code>\n\n"
            "<b>示例：</b>\n"
            "• <code>/delete_posts 123 456 789</code>\n"
            "  删除消息 123、456、789\n\n"
            "• <code>/delete_posts 100-110</code>\n"
            "  删除消息 100 到 110\n\n"
            "• <code>/delete_posts 100-110 150 200-205</code>\n"
            "  混合使用范围和单个ID\n\n"
            "<b>⚠️ 注意：</b>\n"
            "• 只删除数据库记录和搜索索引\n"
            "• 不删除频道消息（需手动删除）\n"
            "• 一次最多删除 50 个帖子",
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        # 解析消息ID列表
        message_ids = set()
        
        for arg in context.args:
            if '-' in arg and arg.replace('-', '').isdigit():
                # 范围格式：100-110
                parts = arg.split('-')
                if len(parts) == 2:
                    start_id = int(parts[0])
                    end_id = int(parts[1])
                    if start_id > end_id:
                        start_id, end_id = end_id, start_id
                    message_ids.update(range(start_id, end_id + 1))
            elif arg.isdigit():
                # 单个ID
                message_ids.add(int(arg))
            else:
                await update.message.reply_text(f"❌ 无效的参数: {arg}")
                return
        
        # 限制数量
        if len(message_ids) > 50:
            await update.message.reply_text(
                f"❌ 一次最多删除 50 个帖子，当前请求删除 {len(message_ids)} 个\n\n"
                "请分批删除或缩小范围"
            )
            return
        
        if len(message_ids) == 0:
            await update.message.reply_text("❌ 未指定有效的消息ID")
            return
        
        # 发送确认消息
        await update.message.reply_text(
            f"⏳ 开始批量删除 {len(message_ids)} 个帖子记录...\n"
            "请稍候..."
        )
        
        # 执行批量删除
        success_count = 0
        failed_count = 0
        not_found_count = 0
        deleted_from_index = 0
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            for msg_id in message_ids:
                try:
                    # 查询帖子是否存在
                    await cursor.execute(
                        "SELECT rowid AS post_id, message_id, related_message_ids FROM published_posts WHERE message_id=?",
                        (msg_id,)
                    )
                    post = await cursor.fetchone()
                    
                    if not post:
                        not_found_count += 1
                        continue
                    
                    # 从搜索索引删除
                    try:
                        from utils.search_engine import get_search_engine
                        search_engine = get_search_engine()
                        if search_engine:
                            search_engine.delete_post(msg_id)
                            deleted_from_index += 1
                            
                            # 删除关联消息
                            if post['related_message_ids']:
                                try:
                                    related_ids = json.loads(post['related_message_ids'])
                                    for related_id in related_ids:
                                        search_engine.delete_post(related_id)
                                except (json.JSONDecodeError, TypeError):
                                    pass
                    except Exception as e:
                        logger.warning(f"从索引删除消息 {msg_id} 失败: {e}")
                    
                    # 从数据库删除
                    await cursor.execute("DELETE FROM published_posts WHERE rowid=?", (post['post_id'],))
                    success_count += 1
                    logger.info(f"批量删除：已删除帖子 message_id={msg_id}")
                    
                except Exception as e:
                    logger.error(f"删除消息 {msg_id} 时出错: {e}")
                    failed_count += 1
            
            await conn.commit()
        
        # 构建结果消息
        result_message = "✅ <b>批量删除完成</b>\n\n"
        result_message += f"📊 <b>统计：</b>\n"
        result_message += f"• 成功删除：{success_count} 个\n"
        if deleted_from_index > 0:
            result_message += f"• 从索引删除：{deleted_from_index} 个\n"
        if not_found_count > 0:
            result_message += f"• 未找到：{not_found_count} 个\n"
        if failed_count > 0:
            result_message += f"• 失败：{failed_count} 个\n"
        
        result_message += f"\n⚠️ <b>注意：</b>\n"
        result_message += "频道中的消息<b>未被删除</b>，如需删除请在频道中手动操作。"
        
        await update.message.reply_text(result_message, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"批量删除失败: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 批量删除失败: {str(e)[:100]}")

