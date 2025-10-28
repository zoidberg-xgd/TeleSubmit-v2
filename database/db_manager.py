"""
数据库管理模块
"""
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import aiosqlite

from config.settings import DB_PATH, TIMEOUT, DB_CACHE_KB

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db():
    """
    数据库连接上下文管理器
    
    Yields:
        aiosqlite.Connection: 数据库连接对象
    """
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    # 优化 SQLite 运行参数，降低 I/O 延迟
    try:
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        await conn.execute("PRAGMA temp_store=MEMORY;")
        # 通过负值设置 KB 为单位的 page cache 大小（默认为 4MB，可通过 DB_CACHE_KB 配置）
        await conn.execute(f"PRAGMA cache_size={-int(DB_CACHE_KB)};")
    except Exception:
        pass
    try:
        yield conn
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise e
    finally:
        await conn.close()

async def init_db():
    """
    初始化数据库
    """
    try:
        async with get_db() as conn:
            # 临时投稿数据表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    user_id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    mode TEXT,
                    image_id TEXT,
                    document_id TEXT,
                    tags TEXT,
                    link TEXT,
                    title TEXT,
                    note TEXT,
                    spoiler TEXT,
                    username TEXT
                )
            ''')
            
            # 已发布帖子表（用于热度统计和搜索）
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS published_posts (
                    message_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    username TEXT,
                    title TEXT,
                    tags TEXT,
                    link TEXT,
                    note TEXT,
                    content_type TEXT,
                    file_ids TEXT,
                    caption TEXT,
                    filename TEXT,
                    publish_time REAL,
                    views INTEGER DEFAULT 0,
                    forwards INTEGER DEFAULT 0,
                    reactions INTEGER DEFAULT 0,
                    heat_score REAL DEFAULT 0,
                    last_update REAL,
                    related_message_ids TEXT
                )
            ''')
            
            # 创建索引以提升查询性能
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_heat_score ON published_posts(heat_score DESC)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_publish_time ON published_posts(publish_time DESC)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON published_posts(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tags ON published_posts(tags)')
            
            await conn.commit()
            logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"初始化数据库时出错: {e}")
        raise

async def cleanup_old_data():
    """
    清理过期的会话数据
    """
    try:
        # 首先检查表是否存在
        async with aiosqlite.connect(DB_PATH) as conn:
            c = await conn.cursor()
            await c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions'")
            table_exists = await c.fetchone()
            
        if not table_exists:
            logger.warning("submissions 表不存在，跳过清理")
            return
            
        # 如果表存在，执行清理
        async with get_db() as conn:
            c = await conn.cursor()
            cutoff = datetime.now().timestamp() - TIMEOUT
            await c.execute("DELETE FROM submissions WHERE timestamp < ?", (cutoff,))
            logger.info("已清理过期数据")
    except Exception as e:
        logger.error(f"清理过期数据失败: {e}")