#!/usr/bin/env python3
"""
数据库迁移脚本：为 published_posts 表添加 filename 字段

用法：python migrate_add_filename.py
"""
import asyncio
import aiosqlite
import logging
from config.settings import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def migrate():
    """执行数据库迁移"""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            
            # 检查 filename 列是否已存在
            await cursor.execute("PRAGMA table_info(published_posts)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'filename' in column_names:
                logger.info("✓ filename 字段已存在，无需迁移")
                return
            
            # 添加 filename 字段
            logger.info("正在添加 filename 字段到 published_posts 表...")
            await cursor.execute('''
                ALTER TABLE published_posts ADD COLUMN filename TEXT
            ''')
            await conn.commit()
            logger.info("✓ 成功添加 filename 字段")
            
            # 统计现有记录数
            await cursor.execute("SELECT COUNT(*) FROM published_posts")
            count = (await cursor.fetchone())[0]
            logger.info(f"数据库中共有 {count} 条记录")
            
            if count > 0:
                logger.info("提示：运行 migrate_extract_filenames.py 从现有消息中提取文件名")
    
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate())
    logger.info("数据库迁移完成！")

