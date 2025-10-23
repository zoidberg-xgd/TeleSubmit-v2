"""
帖子统计和热度排行模块
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext

from config.settings import CHANNEL_ID, OWNER_ID
from database.db_manager import get_db

logger = logging.getLogger(__name__)


def calculate_heat_score(views, forwards, reactions, publish_time):
    """
    计算帖子热度分数
    
    算法考虑因素：
    1. 浏览数（权重0.3）
    2. 转发数（权重0.4，互动更重要）
    3. 反应数（权重0.3）
    4. 时间衰减（越新的帖子权重越高）
    
    Args:
        views: 浏览数
        forwards: 转发数
        reactions: 反应数
        publish_time: 发布时间戳
    
    Returns:
        float: 热度分数
    """
    # 基础分数
    base_score = (views * 0.3) + (forwards * 10 * 0.4) + (reactions * 5 * 0.3)
    
    # 时间衰减因子（使用半衰期算法）
    now = datetime.now().timestamp()
    age_days = (now - publish_time) / 86400  # 转换为天数
    time_decay = 2 ** (-age_days / 7)  # 7天半衰期
    
    # 最终热度分数
    heat_score = base_score * time_decay
    
    return heat_score


async def get_post_statistics(context: CallbackContext, message_id: int):
    """
    获取单个帖子的统计信息
    
    注意：此功能需要机器人是频道管理员，或者频道是公开的
    
    Args:
        context: 回调上下文
        message_id: 消息ID
        
    Returns:
        dict: 包含views, forwards, reactions的字典，失败返回None
    """
    try:
        # Telegram Bot API 中，获取频道消息的统计信息
        # 需要机器人具有频道管理员权限
        
        # 尝试获取消息对象（可能包含统计信息）
        try:
            # 方法1：尝试直接获取消息（需要管理员权限）
            message = await context.bot.get_chat(CHANNEL_ID)
            
            # 由于Telegram Bot API限制，我们无法直接获取单条消息的统计
            # 这里使用一个变通方案：复制消息到临时位置查看
            # 注意：这需要OWNER_ID存在
            if not OWNER_ID:
                logger.warning("未设置OWNER_ID，无法获取帖子统计")
                return None
            
            # 转发消息到所有者私聊（用于获取统计信息）
            forwarded = await context.bot.forward_message(
                chat_id=OWNER_ID,
                from_chat_id=CHANNEL_ID,
                message_id=message_id
            )
            
            # 从转发的消息获取统计
            views = getattr(forwarded, 'views', 0) or 0
            forwards = getattr(forwarded, 'forwards', 0) or 0
            
            # 统计反应数（如果频道启用了反应）
            reactions = 0
            if hasattr(forwarded, 'reactions') and forwarded.reactions:
                for reaction in forwarded.reactions:
                    reactions += reaction.total_count
            
            # 删除转发的消息以保持私聊整洁
            try:
                await context.bot.delete_message(chat_id=OWNER_ID, message_id=forwarded.message_id)
            except:
                pass
            
            return {
                'views': views,
                'forwards': forwards,
                'reactions': reactions
            }
        except Exception as e:
            logger.error(f"获取帖子 {message_id} 统计失败: {e}")
            return None
            
    except Exception as e:
        logger.error(f"获取帖子统计时发生错误: {e}")
        return None


async def update_post_stats(context: CallbackContext):
    """
    定期更新频道帖子统计数据
    
    这个函数会被定时任务调用，用于更新所有活跃帖子的统计信息
    
    Args:
        context: 回调上下文
    """
    try:
        logger.info("开始更新帖子统计数据...")
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            # 获取最近30天的帖子（避免过度请求API）
            cutoff_time = (datetime.now() - timedelta(days=30)).timestamp()
            await cursor.execute(
                "SELECT message_id, publish_time FROM published_posts WHERE publish_time > ?",
                (cutoff_time,)
            )
            posts = await cursor.fetchall()
            
            updated_count = 0
            failed_count = 0
            
            for post in posts:
                message_id = post['message_id']
                publish_time = post['publish_time']
                
                # 获取帖子统计信息
                stats = await get_post_statistics(context, message_id)
                
                if stats:
                    # 计算热度分数
                    heat_score = calculate_heat_score(
                        views=stats['views'],
                        forwards=stats['forwards'],
                        reactions=stats['reactions'],
                        publish_time=publish_time
                    )
                    
                    # 更新数据库
                    await cursor.execute("""
                        UPDATE published_posts 
                        SET views = ?, forwards = ?, reactions = ?, 
                            heat_score = ?, last_update = ?
                        WHERE message_id = ?
                    """, (
                        stats['views'], stats['forwards'], stats['reactions'],
                        heat_score, datetime.now().timestamp(), message_id
                    ))
                    updated_count += 1
                else:
                    failed_count += 1
                
                # 避免API限制，每次请求后休眠
                await asyncio.sleep(2)
            
            await conn.commit()
            logger.info(f"统计数据更新完成：成功 {updated_count} 个，失败 {failed_count} 个")
            
    except Exception as e:
        logger.error(f"更新统计数据失败: {e}")


async def get_hot_posts(update: Update, context: CallbackContext):
    """
    获取热门帖子排行
    
    命令格式：
    /hot [数量] [时间范围]
    
    示例：
    /hot - 查看热门帖子（默认10个）
    /hot 20 - 查看前20个热门帖子
    /hot 10 week - 查看本周前10个热门帖子
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    user_id = update.effective_user.id
    
    try:
        # 解析参数
        args = context.args
        limit = 10  # 默认10个
        time_filter = None  # 时间过滤：day, week, month, all
        
        if args:
            # 第一个参数可能是数量
            if args[0].isdigit():
                limit = int(args[0])
                limit = min(limit, 50)  # 最多50个
                
                # 第二个参数可能是时间范围
                if len(args) > 1:
                    time_filter = args[1].lower()
            else:
                # 第一个参数是时间范围
                time_filter = args[0].lower()
        
        # 构建查询
        query = "SELECT * FROM published_posts WHERE 1=1"
        query_params = []
        
        # 时间过滤
        if time_filter == 'day':
            cutoff = (datetime.now() - timedelta(days=1)).timestamp()
            query += " AND publish_time > ?"
            query_params.append(cutoff)
            time_desc = "今日"
        elif time_filter == 'week':
            cutoff = (datetime.now() - timedelta(days=7)).timestamp()
            query += " AND publish_time > ?"
            query_params.append(cutoff)
            time_desc = "本周"
        elif time_filter == 'month':
            cutoff = (datetime.now() - timedelta(days=30)).timestamp()
            query += " AND publish_time > ?"
            query_params.append(cutoff)
            time_desc = "本月"
        else:
            time_desc = "全部"
        
        # 按热度排序
        query += " ORDER BY heat_score DESC LIMIT ?"
        query_params.append(limit)
        
        async with get_db() as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, query_params)
            hot_posts = await cursor.fetchall()
        
        if not hot_posts:
            await update.message.reply_text(f"📊 暂无{time_desc}热门帖子数据")
            return
        
        # 构建消息
        message = f"🔥 {time_desc}热门帖子 TOP {len(hot_posts)}\n\n"
        
        for idx, post in enumerate(hot_posts, 1):
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
            if len(title) > 30:
                title = title[:27] + '...'
            
            message += (
                f"{idx}. {title}\n"
                f"   {tags_preview}\n"
                f"   📊 浏览: {post['views']} | 转发: {post['forwards']}"
            )
            
            if post['reactions'] > 0:
                message += f" | 反应: {post['reactions']}"
            
            message += f"\n   🔥 热度: {post['heat_score']:.1f}\n"
            message += f"   🔗 {post_link}\n\n"
            
            # 防止消息过长
            if len(message) > 3500:
                message += "...\n\n更多帖子请使用 /search 搜索"
                break
        
        message += f"\n💡 提示：使用 /hot <数量> <时间> 自定义查询\n"
        message += f"时间范围：day(今日)、week(本周)、month(本月)"
        
        await update.message.reply_text(message, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"获取热门帖子失败: {e}")
        await update.message.reply_text("❌ 获取热门帖子失败，请稍后重试")


async def get_user_stats(update: Update, context: CallbackContext):
    """
    获取用户投稿统计
    
    命令格式：
    /mystats - 查看自己的投稿统计
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    user_id = update.effective_user.id
    
    try:
        async with get_db() as conn:
            cursor = await conn.cursor()
            
            # 获取用户的所有投稿
            await cursor.execute(
                "SELECT * FROM published_posts WHERE user_id = ? ORDER BY publish_time DESC",
                (user_id,)
            )
            user_posts = await cursor.fetchall()
        
        if not user_posts:
            await update.message.reply_text("📊 您还没有发布过投稿")
            return
        
        # 统计数据
        total_posts = len(user_posts)
        total_views = sum(post['views'] for post in user_posts)
        total_forwards = sum(post['forwards'] for post in user_posts)
        total_reactions = sum(post['reactions'] for post in user_posts)
        
        # 最热的帖子
        hottest_post = max(user_posts, key=lambda x: x['heat_score'])
        
        # 生成链接
        if CHANNEL_ID.startswith('@'):
            channel_username = CHANNEL_ID.lstrip('@')
            hottest_link = f"https://t.me/{channel_username}/{hottest_post['message_id']}"
        else:
            hottest_link = f"消息ID: {hottest_post['message_id']}"
        
        message = (
            f"📊 您的投稿统计\n\n"
            f"📝 总投稿数：{total_posts}\n"
            f"👀 总浏览数：{total_views}\n"
            f"📤 总转发数：{total_forwards}\n"
            f"❤️ 总反应数：{total_reactions}\n\n"
            f"🔥 最热帖子：\n"
            f"   标题：{hottest_post['title'] or '无标题'}\n"
            f"   热度：{hottest_post['heat_score']:.1f}\n"
            f"   链接：{hottest_link}\n\n"
            f"💡 使用 /hot 查看全站热门帖子"
        )
        
        await update.message.reply_text(message, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {e}")
        await update.message.reply_text("❌ 获取统计失败，请稍后重试")

