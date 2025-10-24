"""
帖子搜索和标签管理模块
"""
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from whoosh.query import DateRange

from config.settings import CHANNEL_ID
from database.db_manager import get_db
from utils.search_engine import get_search_engine

logger = logging.getLogger(__name__)


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
            except:
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
            
            message += (
                f"{idx}. {title}\n"
                f"   {tags_preview}\n"
                f"   📅 {publish_date} | 👀 {hit.views} | 🔥 {hit.heat_score:.0f}\n"
                f"   🔗 {post_link}\n\n"
            )
            
            # 防止消息过长
            if len(message) > 3500:
                message += "...\n\n结果过多，请使用更具体的关键词"
                break
        
        await update.message.reply_text(message, disable_web_page_preview=True, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"搜索帖子失败: {e}", exc_info=True)
        await update.message.reply_text("❌ 搜索失败，请稍后重试")


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
            except:
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
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    user_id = update.effective_user.id
    
    try:
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
            await update.message.reply_text(
                "📝 您还没有发布过投稿\n\n"
                "使用 /submit 开始创建您的第一篇投稿！"
            )
            return
        
        # 构建消息
        message = f"📝 我的投稿（最近 {len(user_posts)} 篇）\n\n"
        
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
            except:
                tags_preview = ""
            
            title = post['title'] or '无标题'
            # 标题过长则截断
            if len(title) > 40:
                title = title[:37] + '...'
            
            # 发布时间
            publish_date = datetime.fromtimestamp(post['publish_time']).strftime('%Y-%m-%d %H:%M')
            
            message += (
                f"{idx}. {title}\n"
                f"   {tags_preview}\n"
                f"   📅 {publish_date}\n"
                f"   📊 浏览 {post['views']} | 转发 {post['forwards']} | 热度 {post['heat_score']:.0f}\n"
                f"   🔗 {post_link}\n\n"
            )
            
            # 防止消息过长
            if len(message) > 3500:
                message += f"...\n\n还有更多投稿，使用 /myposts {limit + 10} 查看更多"
                break
        
        message += "\n💡 使用 /mystats 查看完整统计"
        
        await update.message.reply_text(message, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"获取用户帖子失败: {e}")
        await update.message.reply_text("❌ 获取帖子列表失败，请稍后重试")


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

