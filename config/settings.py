"""
配置文件读取和变量定义模块
"""
import os
import configparser
import logging

logger = logging.getLogger(__name__)

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')

# 读取配置文件
config = configparser.ConfigParser()

# 安全读取配置文件
if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH)
    logger.info(f"已加载配置文件: {CONFIG_PATH}")
else:
    logger.warning(f"⚠️ 配置文件 {CONFIG_PATH} 不存在，将仅使用环境变量")

# 辅助函数：安全获取配置
def get_config(section, key, fallback=None):
    """安全获取配置值"""
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback

def get_config_int(section, key, fallback=0):
    """安全获取整数配置值"""
    try:
        return config.getint(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback

def get_config_bool(section, key, fallback=False):
    """安全获取布尔配置值"""
    try:
        return config.getboolean(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback

# 从环境变量或配置文件获取配置（环境变量优先）
TOKEN = os.getenv('TOKEN') or get_config('BOT', 'TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID') or get_config('BOT', 'CHANNEL_ID')
DB_PATH = get_config('BOT', 'DB_PATH', fallback='data/submissions.db')
TIMEOUT = int(os.getenv('TIMEOUT', get_config_int('BOT', 'TIMEOUT', 300)))
ALLOWED_TAGS = int(os.getenv('ALLOWED_TAGS', get_config_int('BOT', 'ALLOWED_TAGS', 30)))
NET_TIMEOUT = 120   # 网络请求超时时间（秒）

# OWNER_ID 需要转换为整数类型
_owner_id_str = os.getenv('OWNER_ID') or get_config('BOT', 'OWNER_ID')
try:
    OWNER_ID = int(_owner_id_str) if _owner_id_str else None
except (ValueError, TypeError):
    OWNER_ID = None
    logger.warning(f"OWNER_ID 配置无效，无法转换为整数: {_owner_id_str}")

# ADMIN_IDS 管理员ID列表（用于管理命令）
_admin_ids_str = os.getenv('ADMIN_IDS') or get_config('BOT', 'ADMIN_IDS', fallback='')
ADMIN_IDS = []
if _admin_ids_str:
    try:
        # 支持逗号分隔的多个ID
        ADMIN_IDS = [int(id.strip()) for id in _admin_ids_str.split(',') if id.strip()]
    except (ValueError, TypeError):
        logger.warning(f"ADMIN_IDS 配置无效: {_admin_ids_str}")
        ADMIN_IDS = []

# 如果设置了 OWNER_ID 且不在 ADMIN_IDS 中，自动添加
if OWNER_ID and OWNER_ID not in ADMIN_IDS:
    ADMIN_IDS.append(OWNER_ID)

SHOW_SUBMITTER = os.getenv('SHOW_SUBMITTER', str(get_config_bool('BOT', 'SHOW_SUBMITTER', True))).lower() in ('true', '1', 'yes')
NOTIFY_OWNER = os.getenv('NOTIFY_OWNER', str(get_config_bool('BOT', 'NOTIFY_OWNER', True))).lower() in ('true', '1', 'yes')
BOT_MODE = os.getenv('BOT_MODE') or get_config('BOT', 'BOT_MODE', fallback='MIXED')

# 允许的文件类型配置
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES') or get_config('BOT', 'ALLOWED_FILE_TYPES', fallback='*')

# 搜索引擎配置
SEARCH_INDEX_DIR = os.getenv('SEARCH_INDEX_DIR') or get_config('SEARCH', 'INDEX_DIR', fallback='data/search_index')
SEARCH_ENABLED = os.getenv('SEARCH_ENABLED', str(get_config_bool('SEARCH', 'ENABLED', True))).lower() in ('true', '1', 'yes')
SEARCH_ANALYZER = (os.getenv('SEARCH_ANALYZER') or get_config('SEARCH', 'ANALYZER', fallback='jieba')).strip().lower()
SEARCH_HIGHLIGHT = os.getenv('SEARCH_HIGHLIGHT', str(get_config_bool('SEARCH', 'HIGHLIGHT', False))).lower() in ('true', '1', 'yes')

# 数据库配置
DB_CACHE_KB = int(os.getenv('DB_CACHE_KB', get_config_int('DB', 'CACHE_SIZE_KB', 4096)))  # SQLite page cache，单位KB

# 验证必要配置
if not TOKEN:
    raise ValueError("❌ TOKEN 未设置！请在环境变量或 config.ini 中设置")
if not CHANNEL_ID:
    raise ValueError("❌ CHANNEL_ID 未设置！请在环境变量或 config.ini 中设置")

# 模式常量定义
MODE_MEDIA = 'MEDIA'      # 仅媒体上传
MODE_DOCUMENT = 'DOCUMENT'  # 仅文档上传
MODE_MIXED = 'MIXED'      # 混合模式

# 打印配置信息（调试用）
logger.info(f"配置加载完成:")
logger.info(f"  - BOT_MODE: {BOT_MODE}")
logger.info(f"  - CHANNEL_ID: {CHANNEL_ID}")
logger.info(f"  - DB_PATH: {DB_PATH}")
logger.info(f"  - TIMEOUT: {TIMEOUT}")
logger.info(f"  - OWNER_ID: {OWNER_ID if OWNER_ID else '未设置'}")
logger.info(f"  - ADMIN_IDS: {ADMIN_IDS if ADMIN_IDS else '未设置'}")
logger.info(f"  - ALLOWED_FILE_TYPES: {ALLOWED_FILE_TYPES}")
logger.info(f"  - SEARCH_INDEX_DIR: {SEARCH_INDEX_DIR}")
logger.info(f"  - SEARCH_ENABLED: {SEARCH_ENABLED}")
logger.info(f"  - SEARCH_ANALYZER: {SEARCH_ANALYZER}")
logger.info(f"  - SEARCH_HIGHLIGHT: {SEARCH_HIGHLIGHT}")
logger.info(f"  - DB_CACHE_KB: {DB_CACHE_KB}")