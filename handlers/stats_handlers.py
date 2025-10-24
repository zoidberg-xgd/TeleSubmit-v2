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
from utils.heat_calculator import calculate_multi_message_heat, get_quality_metrics

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
            except Exception as e:
                logger.debug(f"无法删除转发消息: {e}")
            
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
    支持多组媒体：累加所有相关消息的统计数据
    
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
                "SELECT message_id, publish_time, related_message_ids FROM published_posts WHERE publish_time > ?",
                (cutoff_time,)
            )
            posts = await cursor.fetchall()
            
            updated_count = 0
            failed_count = 0
            
            for post in posts:
                message_id = post['message_id']
                publish_time = post['publish_time']
                related_ids_json = post['related_message_ids']
                
                # 获取主消息的统计信息
                main_stats = await get_post_statistics(context, message_id)
                
                if main_stats:
                    related_stats_list = []
                    
                    # 如果有关联消息（多组媒体），获取它们的统计
                    if related_ids_json:
                        try:
                            related_ids = json.loads(related_ids_json)
                            logger.info(f"帖子 {message_id} 有 {len(related_ids)} 个关联消息，使用智能算法计算热度")
                            
                            for related_id in related_ids:
                                related_stats = await get_post_statistics(context, related_id)
                                if related_stats:
                                    related_stats_list.append(related_stats)
                                await asyncio.sleep(1)  # 避免API限制
                                
                        except json.JSONDecodeError:
                            logger.warning(f"解析关联消息ID失败: {related_ids_json}")
                    
                    # 使用智能算法计算热度（避免重复计数）
                    heat_result = calculate_multi_message_heat(
                        main_stats=main_stats,
                        related_stats_list=related_stats_list,
                        publish_time=publish_time
                    )
                    
                    # 获取质量指标
                    quality_metrics = get_quality_metrics(main_stats, related_stats_list)
                    
                    logger.info(
                        f"帖子 {message_id} 热度计算完成 | "
                        f"有效浏览: {heat_result['effective_views']:.0f} | "
                        f"有效转发: {heat_result['effective_forwards']} | "
                        f"有效反应: {heat_result['effective_reactions']:.0f} | "
                        f"热度: {heat_result['heat_score']:.2f} | "
                        f"互动率: {quality_metrics['engagement_rate']:.2%} | "
                        f"完成率: {quality_metrics['completion_rate']:.2%}"
                    )
                    
                    # 更新数据库
                    await cursor.execute("""
                        UPDATE published_posts 
                        SET views = ?, forwards = ?, reactions = ?, 
                            heat_score = ?, last_update = ?
                        WHERE message_id = ?
                    """, (
                        int(heat_result['effective_views']),
                        int(heat_result['effective_forwards']),
                        int(heat_result['effective_reactions']),
                        heat_result['heat_score'], 
                        datetime.now().timestamp(), 
                        message_id
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
    获取热门帖子排行 - 只显示主贴，优化预览样式
    
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
        
        # 构建查询 - 只查询主贴（有标题或至少有内容的帖子）
        # published_posts 表中存储的都是主贴，不包含多组媒体的后续消息
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
        
        # 构建消息 - 优化显示格式
        message = f"🔥 <b>{time_desc}热门帖子 TOP {len(hot_posts)}</b>\n\n"
        
        for idx, post in enumerate(hot_posts, 1):
            # 生成帖子链接
            if CHANNEL_ID.startswith('@'):
                channel_username = CHANNEL_ID.lstrip('@')
                post_link = f"https://t.me/{channel_username}/{post['message_id']}"
            else:
                post_link = f"消息ID: {post['message_id']}"
            
            # 解析标签
            tags_display = ""
            if post['tags']:
                try:
                    # 尝试解析JSON格式的标签
                    tags = json.loads(post['tags'])
                    if isinstance(tags, list):
                        tags_display = ' '.join([f"#{tag}" for tag in tags[:5]])  # 显示最多5个标签
                    else:
                        tags_display = post['tags']  # 如果不是列表，直接显示
                except (json.JSONDecodeError, TypeError, ValueError):
                    # 如果解析失败，假设是空格分隔的字符串
                    tags_list = post['tags'].split()[:5]
                    tags_display = ' '.join([f"#{tag.lstrip('#')}" for tag in tags_list])
            
            # 处理标题
            title = post['title'] or '无标题'
            if len(title) > 40:
                title = title[:37] + '...'
            
            # 处理简介（note）
            note_preview = ""
            if post['note']:
                note = post['note'].strip()
                if note:
                    # 去掉换行，限制长度
                    note = note.replace('\n', ' ').replace('\r', ' ')
                    if len(note) > 60:
                        note = note[:57] + '...'
                    note_preview = f"\n   💬 {note}"
            
            # 格式化发布时间
            publish_time = datetime.fromtimestamp(post['publish_time'])
            time_ago = _format_time_ago(publish_time)
            
            # 构建单个帖子的显示
            message += f"<b>{idx}.</b> <a href='{post_link}'>{title}</a>\n"
            
            if tags_display:
                message += f"   🏷 {tags_display}\n"
            
            if note_preview:
                message += note_preview + "\n"
            
            # 统计数据
            stats_parts = []
            if post['views'] > 0:
                stats_parts.append(f"👁 {_format_number(post['views'])}")
            if post['forwards'] > 0:
                stats_parts.append(f"📤 {post['forwards']}")
            if post['reactions'] > 0:
                stats_parts.append(f"❤️ {post['reactions']}")
            
            if stats_parts:
                message += f"   📊 {' | '.join(stats_parts)}\n"
            
            # 热度和时间
            message += f"   🔥 热度: <code>{post['heat_score']:.1f}</code> • 🕐 {time_ago}\n"
            message += "\n"
            
            # 防止消息过长
            if len(message) > 3500:
                message += "...\n\n💡 更多帖子请使用 /search 搜索"
                break
        
        message += f"━━━━━━━━━━━━━━━\n"
        message += f"💡 使用 <code>/hot &lt;数量&gt; &lt;时间&gt;</code> 自定义查询\n"
        message += f"⏰ 时间范围：day(今日)、week(本周)、month(本月)"
        
        await update.message.reply_text(
            message, 
            disable_web_page_preview=True,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"获取热门帖子失败: {e}")
        await update.message.reply_text("❌ 获取热门帖子失败，请稍后重试")


def _format_time_ago(publish_time: datetime) -> str:
    """
    格式化时间为"多久前"的形式
    
    Args:
        publish_time: 发布时间
        
    Returns:
        str: 格式化的时间字符串
    """
    now = datetime.now()
    delta = now - publish_time
    
    if delta.days > 30:
        months = delta.days // 30
        return f"{months}月前"
    elif delta.days > 0:
        return f"{delta.days}天前"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}小时前"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"


def _format_number(num: int) -> str:
    """
    格式化数字，大数字使用k、w等单位
    
    Args:
        num: 要格式化的数字
        
    Returns:
        str: 格式化后的字符串
    """
    if num >= 10000:
        return f"{num / 10000:.1f}w"
    elif num >= 1000:
        return f"{num / 1000:.1f}k"
    else:
        return str(num)


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

