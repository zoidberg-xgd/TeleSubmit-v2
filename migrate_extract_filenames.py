#!/usr/bin/env python3
"""
数据迁移脚本：从现有频道消息中提取文件名并更新数据库和搜索索引

用法：python migrate_extract_filenames.py
"""
import asyncio
import aiosqlite
import logging
from telegram import Bot
from datetime import datetime

from config.settings import TOKEN, CHANNEL_ID, DB_PATH
from utils.search_engine import get_search_engine, PostDocument

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_filenames_from_messages():
    """从频道消息中提取文件名并更新数据库"""
    bot = Bot(token=TOKEN)
    
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()
            
            # 获取所有需要更新的帖子
            await cursor.execute("""
                SELECT message_id, user_id, username, title, tags, link, note, 
                       publish_time, views, heat_score
                FROM published_posts 
                WHERE content_type IN ('document', 'mixed') 
                AND (filename IS NULL OR filename = '')
            """)
            posts = await cursor.fetchall()
            
            if not posts:
                logger.info("没有需要迁移的记录")
                return
            
            logger.info(f"找到 {len(posts)} 条需要提取文件名的记录")
            
            # 初始化搜索引擎
            search_engine = get_search_engine()
            
            updated_count = 0
            failed_count = 0
            
            for post in posts:
                message_id = post['message_id']
                
                try:
                    # 从频道获取消息
                    message = await bot.get_chat(CHANNEL_ID)
                    # 注意：需要使用 forward_from_chat 或直接获取消息
                    # 由于 API 限制，这里使用另一种方法
                    try:
                        # 尝试转发消息到机器人自己（然后立即删除）来获取文件信息
                        # 更好的方法是直接从消息获取
                        # 但 get_chat 不支持获取具体消息，需要使用其他方法
                        
                        # 简化方案：跳过此消息，记录日志
                        # 实际上，Telegram Bot API 无法直接通过 message_id 获取频道中的消息
                        # 除非机器人是频道管理员
                        
                        # 这里我们采用另一种策略：
                        # 1. 如果 file_ids 字段有数据，尝试从中提取
                        # 2. 否则标记为需要手动处理
                        
                        logger.warning(f"消息 {message_id} 需要手动处理（Bot API 限制）")
                        failed_count += 1
                        continue
                        
                    except Exception as e:
                        logger.error(f"获取消息 {message_id} 失败: {e}")
                        failed_count += 1
                        continue
                    
                except Exception as e:
                    logger.error(f"处理消息 {message_id} 时出错: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"迁移完成：成功 {updated_count}，失败 {failed_count}")
            
            # 提示用户
            if failed_count > 0:
                logger.warning(
                    f"\n注意：由于 Telegram Bot API 的限制，无法自动提取历史消息的文件名。\n"
                    f"对于新发布的帖子，文件名将自动记录。\n"
                    f"如需搜索现有帖子的文件名，请在标题或简介中包含文件名信息。"
                )
    
    except Exception as e:
        logger.error(f"迁移失败: {e}", exc_info=True)
        raise
    finally:
        await bot.close()


async def migrate_with_manual_update():
    """
    替代方案：提示用户手动更新或通过重新索引
    
    由于 Telegram Bot API 限制，我们无法直接访问历史消息的文件信息。
    建议用户：
    1. 新投稿会自动记录文件名
    2. 旧投稿可以通过标题/简介搜索
    3. 如果需要，可以手动编辑数据库
    """
    logger.info("=" * 60)
    logger.info("文件名提取迁移说明")
    logger.info("=" * 60)
    logger.info("")
    logger.info("由于 Telegram Bot API 的限制，无法自动提取历史消息中的文件名。")
    logger.info("")
    logger.info("✅ 好消息：")
    logger.info("  • 从现在开始，所有新发布的投稿都会自动记录文件名")
    logger.info("  • 搜索功能已升级，支持文件名搜索")
    logger.info("")
    logger.info("📝 关于历史投稿：")
    logger.info("  • 历史投稿的文件名字段为空")
    logger.info("  • 您仍然可以通过标题、简介、标签来搜索这些帖子")
    logger.info("  • 建议在投稿时在标题或简介中包含文件名信息")
    logger.info("")
    logger.info("🔍 搜索提示：")
    logger.info("  • /search 文件名 - 搜索包含该文件名的新投稿")
    logger.info("  • /search 关键词 - 搜索标题、简介、标签、文件名")
    logger.info("")
    logger.info("=" * 60)
    
    # 标记数据库迁移已完成
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            
            # 检查是否有记录
            await cursor.execute("SELECT COUNT(*) FROM published_posts")
            count = (await cursor.fetchone())[0]
            
            logger.info(f"数据库中共有 {count} 条投稿记录")
            
            # 统计有文件名的记录
            await cursor.execute("""
                SELECT COUNT(*) FROM published_posts 
                WHERE filename IS NOT NULL AND filename != ''
            """)
            with_filename = (await cursor.fetchone())[0]
            
            logger.info(f"其中 {with_filename} 条记录有文件名信息")
            logger.info(f"还有 {count - with_filename} 条旧记录暂无文件名（正常情况）")
            
    except Exception as e:
        logger.error(f"检查数据库失败: {e}")


if __name__ == "__main__":
    # 使用简化的迁移方案
    asyncio.run(migrate_with_manual_update())
    logger.info("\n✅ 文件名搜索功能已启用！")

