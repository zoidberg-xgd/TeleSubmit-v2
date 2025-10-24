#!/usr/bin/env python3
"""
数据库性能优化脚本
添加索引以提升查询性能
"""
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def optimize_database():
    """优化数据库性能"""
    
    print('='*80)
    print('🔧 数据库性能优化')
    print('='*80)
    print()
    
    # 优化主数据库
    optimize_main_db()
    
    # 优化会话数据库
    optimize_session_db()
    
    print()
    print('='*80)
    print('✅ 数据库优化完成')
    print('='*80)

def optimize_main_db():
    """优化主数据库（submissions.db）"""
    print('📊 优化 submissions.db...')
    
    try:
        conn = sqlite3.connect('data/submissions.db')
        c = conn.cursor()
        
        # 检查现有索引
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = {row[0] for row in c.fetchall()}
        
        # 需要创建的索引
        indexes = [
            ('idx_published_posts_user_id', 'published_posts', 'user_id'),
            ('idx_published_posts_publish_time', 'published_posts', 'publish_time'),
            ('idx_published_posts_heat_score', 'published_posts', 'heat_score'),
            ('idx_published_posts_message_id', 'published_posts', 'message_id'),
            ('idx_published_posts_username', 'published_posts', 'username'),
        ]
        
        created = 0
        for idx_name, table, column in indexes:
            if idx_name not in existing_indexes:
                try:
                    c.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})')
                    logger.info(f'  ✓ 创建索引: {idx_name}')
                    created += 1
                except sqlite3.Error as e:
                    logger.warning(f'  ⚠️ 索引创建失败 {idx_name}: {e}')
            else:
                logger.info(f'  → 索引已存在: {idx_name}')
        
        # 分析表以更新统计信息
        c.execute('ANALYZE published_posts')
        
        # 清理和优化
        c.execute('VACUUM')
        
        conn.commit()
        conn.close()
        
        print(f'  ✅ 创建了 {created} 个新索引')
        print(f'  ✅ 已运行 ANALYZE 和 VACUUM')
        
    except FileNotFoundError:
        logger.warning('  ⚠️ data/submissions.db 不存在')
    except sqlite3.Error as e:
        logger.error(f'  ❌ 优化失败: {e}')

def optimize_session_db():
    """优化会话数据库（user_sessions.db）"""
    print()
    print('📊 优化 user_sessions.db...')
    
    try:
        conn = sqlite3.connect('user_sessions.db')
        c = conn.cursor()
        
        # 检查现有索引
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = {row[0] for row in c.fetchall()}
        
        # 需要创建的索引
        indexes = [
            ('idx_user_sessions_last_activity', 'user_sessions', 'last_activity'),
            ('idx_user_sessions_state', 'user_sessions', 'state'),
        ]
        
        created = 0
        for idx_name, table, column in indexes:
            if idx_name not in existing_indexes:
                try:
                    c.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})')
                    logger.info(f'  ✓ 创建索引: {idx_name}')
                    created += 1
                except sqlite3.Error as e:
                    logger.warning(f'  ⚠️ 索引创建失败 {idx_name}: {e}')
            else:
                logger.info(f'  → 索引已存在: {idx_name}')
        
        # 清理过期会话（超过7天未活动）
        cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)
        c.execute('DELETE FROM user_sessions WHERE last_activity < ?', (cutoff_time,))
        deleted = c.rowcount
        
        # 分析表
        c.execute('ANALYZE user_sessions')
        
        conn.commit()
        conn.close()
        
        # VACUUM 需要在单独的连接中执行
        conn = sqlite3.connect('user_sessions.db')
        conn.execute('VACUUM')
        conn.close()
        
        print(f'  ✅ 创建了 {created} 个新索引')
        print(f'  ✅ 清理了 {deleted} 个过期会话')
        print(f'  ✅ 已运行 ANALYZE 和 VACUUM')
        
    except FileNotFoundError:
        logger.warning('  ⚠️ user_sessions.db 不存在')
    except sqlite3.Error as e:
        logger.error(f'  ❌ 优化失败: {e}')

def show_db_stats():
    """显示数据库统计信息"""
    print()
    print('📈 数据库统计信息:')
    print()
    
    try:
        conn = sqlite3.connect('data/submissions.db')
        c = conn.cursor()
        
        # 统计投稿数量
        c.execute('SELECT COUNT(*) FROM published_posts')
        post_count = c.fetchone()[0]
        
        # 数据库大小
        c.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = c.fetchone()[0]
        
        # 索引数量
        c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        index_count = c.fetchone()[0]
        
        print(f'  投稿数量: {post_count:,}')
        print(f'  数据库大小: {db_size / 1024 / 1024:.2f} MB')
        print(f'  索引数量: {index_count}')
        
        conn.close()
        
    except Exception as e:
        logger.error(f'  ❌ 获取统计信息失败: {e}')

if __name__ == '__main__':
    optimize_database()
    show_db_stats()

