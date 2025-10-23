"""
配置文件读取和变量定义模块
"""
import os
import configparser

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')

# 读取配置文件
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 从环境变量或配置文件获取配置
TOKEN = os.getenv('TOKEN', config.get('BOT', 'TOKEN'))
CHANNEL_ID = os.getenv('CHANNEL_ID', config.get('BOT', 'CHANNEL_ID'))
DB_PATH = config.get('BOT', 'DB_PATH', fallback='submissions.db')
TIMEOUT = config.getint('BOT', 'TIMEOUT', fallback=300)    # 会话超时时间（秒）
ALLOWED_TAGS = config.getint('BOT', 'ALLOWED_TAGS', fallback=10)
NET_TIMEOUT = 120   # 网络请求超时时间（秒）
OWNER_ID = config.get('BOT', 'OWNER_ID', fallback=None)  # 机器人所有者ID
SHOW_SUBMITTER = config.getboolean('BOT', 'SHOW_SUBMITTER', fallback=True)  # 是否显示投稿人信息
NOTIFY_OWNER = config.getboolean('BOT', 'NOTIFY_OWNER', fallback=True)  # 是否向所有者发送投稿通知

# 机器人模式: MEDIA (仅媒体), DOCUMENT (仅文档), MIXED (混合模式)
BOT_MODE = config.get('BOT', 'BOT_MODE', fallback='MIXED')

# 模式常量定义
MODE_MEDIA = 'MEDIA'      # 仅媒体上传
MODE_DOCUMENT = 'DOCUMENT'  # 仅文档上传
MODE_MIXED = 'MIXED'      # 混合模式