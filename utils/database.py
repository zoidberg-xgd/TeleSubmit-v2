import logging
import sqlite3
import time
import threading
from functools import wraps
from typing import Dict, Any

logger = logging.getLogger(__name__)

# 连接锁，确保线程安全
db_lock = threading.RLock()

# 重试装饰器
def retry_on_db_error(max_attempts=3, delay=1):
    """数据库操作重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except sqlite3.Error as e:
                    last_error = e
                    logger.warning(f"数据库操作失败 (第{attempt+1}次尝试): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        logger.info(f"重试数据库操作...")
                    else:
                        logger.error(f"数据库操作失败 (达到最大尝试次数): {e}")
            raise last_error  # 重试全部失败后抛出最后的异常
        return wrapper
    return decorator

# 初始化数据库连接
@retry_on_db_error()
def get_connection():
    """获取数据库连接，确保线程安全"""
    try:
        conn = sqlite3.connect("telesubmit.db", timeout=10)  # 增加超时时间
        conn.row_factory = sqlite3.Row
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        # 启用WAL模式，提高并发性能
        conn.execute("PRAGMA journal_mode = WAL")
        return conn
    except sqlite3.Error as e:
        logger.error(f"无法连接到数据库: {e}")
        raise

# 确保数据库和表格已创建
@retry_on_db_error()
def initialize_database():
    """初始化用户会话和黑名单数据库"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 创建用户会话表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                last_activity REAL
            )
            ''')
            
            # 创建黑名单表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS blacklist (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                added_at REAL
            )
            ''')
            
            conn.commit()
            logger.info("成功初始化用户会话和黑名单数据库")
        except sqlite3.Error as e:
            logger.error(f"初始化用户会话数据库失败: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

# 用户会话相关操作
@retry_on_db_error()
def save_user_state(user_id, state, data=None):
    """保存用户会话状态"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            timestamp = time.time()
            
            cursor.execute(
                "INSERT OR REPLACE INTO user_sessions (user_id, state, data, last_activity) VALUES (?, ?, ?, ?)",
                (user_id, state, data, timestamp)
            )
            
            conn.commit()
            logger.debug(f"已保存用户 {user_id} 的状态: {state}")
            return True
        except sqlite3.Error as e:
            logger.error(f"保存用户状态失败 (用户ID: {user_id}): {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

@retry_on_db_error()
def get_user_state(user_id):
    """获取用户会话状态"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT state, data, last_activity FROM user_sessions WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                # 更新最后活动时间
                timestamp = time.time()
                cursor.execute("UPDATE user_sessions SET last_activity = ? WHERE user_id = ?", (timestamp, user_id))
                conn.commit()
                
                return {
                    "state": result["state"],
                    "data": result["data"],
                    "last_activity": result["last_activity"]
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"获取用户状态失败 (用户ID: {user_id}): {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

@retry_on_db_error()
def delete_user_state(user_id):
    """删除用户会话状态"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            
            logger.info(f"已删除用户 {user_id} 的会话数据")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"删除用户状态失败 (用户ID: {user_id}): {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

@retry_on_db_error()
def get_all_active_sessions():
    """获取所有活跃会话"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, state, data, last_activity FROM user_sessions")
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "user_id": row["user_id"],
                    "state": row["state"],
                    "data": row["data"],
                    "last_activity": row["last_activity"]
                })
            
            return sessions
        except sqlite3.Error as e:
            logger.error(f"获取所有活跃会话失败: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

# 黑名单相关操作
@retry_on_db_error()
def add_to_blacklist(user_id, reason=None):
    """将用户添加到黑名单"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            timestamp = time.time()
            
            cursor.execute(
                "INSERT OR REPLACE INTO blacklist (user_id, reason, added_at) VALUES (?, ?, ?)",
                (user_id, reason, timestamp)
            )
            
            conn.commit()
            logger.info(f"已将用户 {user_id} 添加到黑名单，原因: {reason}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加用户到黑名单失败 (用户ID: {user_id}): {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

@retry_on_db_error()
def remove_from_blacklist(user_id):
    """从黑名单中移除用户"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM blacklist WHERE user_id = ?", (user_id,))
            conn.commit()
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"已从黑名单中移除用户 {user_id}")
            else:
                logger.warning(f"用户 {user_id} 不在黑名单中，无需移除")
            
            return success
        except sqlite3.Error as e:
            logger.error(f"从黑名单中移除用户失败 (用户ID: {user_id}): {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

def is_blacklisted(user_id: int) -> bool:
    """
    检查用户是否在黑名单中（代理函数，实际调用utils.blacklist模块）
    
    Args:
        user_id: 要检查的用户ID
        
    Returns:
        bool: 用户是否在黑名单中
    """
    try:
        # 引入黑名单模块
        from utils.blacklist import is_blacklisted as bl_check
        return bl_check(user_id)
    except ImportError:
        logger.error("无法导入黑名单模块，默认返回用户不在黑名单")
        return False
    except Exception as e:
        logger.error(f"检查黑名单状态时出错: {str(e)}")
        return False

@retry_on_db_error()
def get_blacklist():
    """获取完整黑名单"""
    with db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, reason, added_at FROM blacklist")
            rows = cursor.fetchall()
            
            blacklist = []
            for row in rows:
                blacklist.append({
                    "user_id": row["user_id"],
                    "reason": row["reason"],
                    "added_at": row["added_at"]
                })
            
            return blacklist
        except sqlite3.Error as e:
            logger.error(f"获取黑名单失败: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

def get_all_user_states() -> Dict[int, Dict[str, Any]]:
    """
    获取所有用户的会话状态
    
    Returns:
        Dict[int, Dict[str, Any]]: 用户ID到会话状态的映射
    """
    try:
        sessions = get_all_active_sessions()
        # 将列表转换为字典格式
        result = {}
        for session in sessions:
            user_id = session.get('user_id')
            if user_id:
                result[user_id] = session
        return result
    except Exception as e:
        logger.error(f"获取所有用户状态失败: {e}")
        return {} 