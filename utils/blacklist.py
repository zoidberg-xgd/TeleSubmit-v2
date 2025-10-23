"""
黑名单管理模块
"""
import logging
import aiosqlite
from typing import List, Set, Optional

from database.db_manager import get_db
from config.settings import OWNER_ID

logger = logging.getLogger(__name__)

# 内存中的黑名单缓存
_blacklist: Set[int] = set()

# 自定义黑名单过滤器函数
def blacklist_filter(update):
    """过滤黑名单用户"""
    if update.effective_user and is_blacklisted(update.effective_user.id):
        logger.warning(f"拦截黑名单用户: {update.effective_user.id}")
        return False
    return True

async def init_blacklist():
    """初始化黑名单表并加载到内存"""
    try:
        async with get_db() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS blacklist (
                    user_id INTEGER PRIMARY KEY,
                    reason TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.commit()
            
            # 加载黑名单到内存
            async with conn.execute("SELECT user_id FROM blacklist") as cursor:
                rows = await cursor.fetchall()
                _blacklist.clear()
                for row in rows:
                    _blacklist.add(row[0])
                    
        logger.info(f"黑名单已初始化，当前有 {len(_blacklist)} 个用户")
    except Exception as e:
        logger.error(f"初始化黑名单时出错: {e}")

async def add_to_blacklist(user_id: int, reason: str = "未指定原因") -> bool:
    """
    添加用户到黑名单
    
    Args:
        user_id: 要添加的用户ID
        reason: 添加原因
        
    Returns:
        bool: 是否成功添加
    """
    try:
        async with get_db() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO blacklist (user_id, reason) VALUES (?, ?)",
                (user_id, reason)
            )
            await conn.commit()
            
        # 更新内存缓存
        _blacklist.add(user_id)
        logger.info(f"已将用户 {user_id} 添加到黑名单，原因: {reason}")
        return True
    except Exception as e:
        logger.error(f"添加用户到黑名单时出错: {e}")
        return False

async def remove_from_blacklist(user_id: int) -> bool:
    """
    从黑名单中移除用户
    
    Args:
        user_id: 要移除的用户ID
        
    Returns:
        bool: 是否成功移除
    """
    try:
        async with get_db() as conn:
            await conn.execute("DELETE FROM blacklist WHERE user_id = ?", (user_id,))
            await conn.commit()
            
            if user_id in _blacklist:
                _blacklist.remove(user_id)
                logger.info(f"已将用户 {user_id} 从黑名单中移除")
                return True
            else:
                logger.info(f"用户 {user_id} 不在黑名单中")
                return False
    except Exception as e:
        logger.error(f"从黑名单中移除用户时出错: {e}")
        return False

async def get_blacklist() -> List[dict]:
    """
    获取完整黑名单
    
    Returns:
        List[dict]: 黑名单用户列表，每个用户包含 user_id, reason, added_at
    """
    try:
        async with get_db() as conn:
            async with conn.execute(
                "SELECT user_id, reason, added_at FROM blacklist ORDER BY added_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {"user_id": row[0], "reason": row[1], "added_at": row[2]}
                    for row in rows
                ]
    except Exception as e:
        logger.error(f"获取黑名单时出错: {e}")
        return []

def is_blacklisted(user_id: int) -> bool:
    """
    检查用户是否在黑名单中
    
    Args:
        user_id: 要检查的用户ID
        
    Returns:
        bool: 用户是否在黑名单中
    """
    return user_id in _blacklist

def is_owner(user_id: int) -> bool:
    """
    检查用户是否为机器人所有者
    
    Args:
        user_id: 要检查的用户ID
        
    Returns:
        bool: 用户是否为机器人所有者
    """
    try:
        # 记录输入参数
        logger.info(f"is_owner被调用 - 检查用户ID: {user_id} (类型: {type(user_id)})")
        
        # 检查user_id是否有效
        if user_id is None:
            logger.warning("is_owner被调用但user_id为None")
            return False
            
        # 首先检查OWNER_ID是否存在
        if not OWNER_ID:
            logger.warning(f"OWNER_ID未设置或为空，用户{user_id}的所有者检查失败")
            return False
        
        # 确保user_id是整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            logger.error(f"user_id无法转换为整数: {user_id}")
            return False
            
        # 确保OWNER_ID是整数或者可以转换为整数
        try:
            owner_id_int = int(OWNER_ID)
        except (ValueError, TypeError):
            logger.error(f"OWNER_ID无法转换为整数: {OWNER_ID}")
            return False
            
        # 使用整数进行直接比较
        result = user_id_int == owner_id_int
        
        # 记录详细的日志
        logger.info(f"所有者检查 - 用户ID: {user_id_int}, OWNER_ID: {owner_id_int}, 结果: {result}")
        
        return result
            
    except Exception as e:
        # 捕获任何可能的异常
        logger.error(f"所有者检查过程中发生错误: {e}", exc_info=True)
        return False

async def manage_blacklist(update, context):
    """
    黑名单管理命令处理
    
    Args:
        update: Telegram 更新对象
        context: 回调上下文
    """
    user_id = update.effective_user.id
    
    # 检查是否为所有者
    if not is_owner(user_id):
        logger.warning(f"非所有者用户 {user_id} 尝试使用黑名单管理命令")
        await update.message.reply_text("⚠️ 只有机器人所有者才能使用此命令")
        return
    
    # 显示帮助信息
    await update.message.reply_text(
        "📋 黑名单管理命令：\n\n"
        "/blacklist_add <user_id> [原因] - 将用户添加到黑名单\n"
        "/blacklist_remove <user_id> - 将用户从黑名单中移除\n"
        "/blacklist_list - 列出所有黑名单用户"
    ) 