#!/usr/bin/env python3
"""
TeleSubmit v2 配置向导
交互式配置脚本，帮助快速部署机器人
"""
import os
import sys
from pathlib import Path

def print_header():
    """打印欢迎头部"""
    print("\n" + "=" * 70)
    print("🤖 TeleSubmit v2 配置向导".center(70))
    print("=" * 70 + "\n")

def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 70)

def get_input(prompt, default=None, required=True):
    """获取用户输入"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        
        if not value and default:
            return default
        
        if not value and required:
            print("❌ 此项为必填项，请输入有效值")
            continue
        
        return value

def validate_token(token):
    """验证 Bot Token 格式"""
    if not token or token == 'your_bot_token_here':
        return False
    
    # 简单格式检查：应该包含冒号
    if ':' not in token:
        return False
    
    parts = token.split(':')
    if len(parts) != 2:
        return False
    
    # 第一部分应该是数字
    if not parts[0].isdigit():
        return False
    
    return True

def validate_channel(channel):
    """验证频道 ID 格式"""
    if not channel or channel == '@your_channel':
        return False
    
    # 应该以 @ 开头或者是负数
    if channel.startswith('@') or channel.startswith('-'):
        return True
    
    return False

def validate_user_id(user_id):
    """验证用户 ID"""
    if not user_id or user_id == 'your_user_id':
        return False
    
    return user_id.isdigit()

def create_config():
    """创建配置文件"""
    print_header()
    
    print("欢迎使用 TeleSubmit v2！")
    print("这个向导将帮助您配置机器人。\n")
    
    # 步骤1：Bot Token
    print_section("步骤 1/3：Telegram Bot Token")
    print("📝 如何获取 Bot Token：")
    print("   1. 在 Telegram 中找 @BotFather")
    print("   2. 发送 /newbot 创建新机器人")
    print("   3. 按提示设置机器人名称和用户名")
    print("   4. 复制获得的 token\n")
    
    while True:
        token = get_input("请输入 Bot Token", required=True)
        if validate_token(token):
            print("✅ Token 格式正确")
            break
        else:
            print("❌ Token 格式不正确，请检查后重新输入")
            print("   正确格式示例：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n")
    
    # 步骤2：频道 ID
    print_section("步骤 2/3：Telegram 频道")
    print("📝 如何获取频道 ID：")
    print("   • 公开频道：使用 @频道用户名（如 @mychannel）")
    print("   • 私有频道：使用频道 ID（如 -1001234567890）")
    print("     获取方法：将 @userinfobot 添加到频道，它会告诉你频道 ID")
    print("\n⚠️  重要：需要将机器人添加为频道管理员！\n")
    
    while True:
        channel = get_input("请输入频道 ID 或用户名", required=True)
        if validate_channel(channel):
            print("✅ 频道 ID 格式正确")
            break
        else:
            print("❌ 频道 ID 格式不正确")
            print("   应该以 @ 开头（如 @mychannel）或以 - 开头（如 -1001234567890）\n")
    
    # 步骤3：所有者 ID
    print_section("步骤 3/3：所有者 User ID")
    print("📝 如何获取您的 User ID：")
    print("   1. 在 Telegram 中找 @userinfobot")
    print("   2. 发送任意消息")
    print("   3. 复制 Bot 返回的您的 ID（纯数字）\n")
    
    while True:
        owner_id = get_input("请输入您的 User ID", required=True)
        if validate_user_id(owner_id):
            print("✅ User ID 格式正确")
            break
        else:
            print("❌ User ID 应该是纯数字\n")
    
    # 可选配置
    print_section("可选配置")
    
    show_submitter = get_input(
        "是否在投稿中显示投稿人信息？(yes/no)", 
        default="yes",
        required=False
    ).lower() in ['yes', 'y', 'true', '1']
    
    notify_owner = get_input(
        "是否向所有者发送新投稿通知？(yes/no)", 
        default="yes",
        required=False
    ).lower() in ['yes', 'y', 'true', '1']
    
    bot_mode = get_input(
        "机器人模式 (MEDIA/DOCUMENT/MIXED)", 
        default="MIXED",
        required=False
    ).upper()
    
    if bot_mode not in ['MEDIA', 'DOCUMENT', 'MIXED']:
        bot_mode = 'MIXED'
    
    # 生成配置文件
    print_section("生成配置文件")
    
    config_content = f"""[BOT]
# Telegram Bot Token (从 @BotFather 获取)
TOKEN = {token}

# 频道 ID (格式: @channel_username 或 -100xxxxxxxxxx)
CHANNEL_ID = {channel}

# 数据库文件路径
DB_PATH = data/submissions.db

# 会话超时时间（秒）
TIMEOUT = 300

# 允许的最大标签数量
ALLOWED_TAGS = 30

# 机器人所有者的 Telegram User ID
OWNER_ID = {owner_id}

# 是否在投稿中显示投稿人信息 (true/false)
SHOW_SUBMITTER = {'true' if show_submitter else 'false'}

# 是否向所有者发送新投稿通知 (true/false)
NOTIFY_OWNER = {'true' if notify_owner else 'false'}

# 机器人模式: MEDIA (仅媒体), DOCUMENT (仅文档), MIXED (混合模式)
BOT_MODE = {bot_mode}

[SEARCH]
# 搜索索引目录
INDEX_DIR = data/search_index

# 是否启用搜索功能
ENABLED = true
"""
    
    config_path = Path('config.ini')
    
    # 如果配置文件已存在，询问是否覆盖
    if config_path.exists():
        overwrite = get_input(
            "\n⚠️  config.ini 已存在，是否覆盖？(yes/no)", 
            default="no",
            required=False
        ).lower() in ['yes', 'y']
        
        if not overwrite:
            print("\n❌ 配置已取消")
            return False
    
    # 写入配置文件
    config_path.write_text(config_content, encoding='utf-8')
    print(f"✅ 配置文件已创建：{config_path.absolute()}")
    
    # 创建必要的目录
    print("\n📁 创建数据目录...")
    Path('data').mkdir(exist_ok=True)
    Path('data/search_index').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    print("✅ 数据目录创建完成")
    
    # 完成
    print("\n" + "=" * 70)
    print("✅ 配置完成！".center(70))
    print("=" * 70)
    
    print("\n📋 下一步操作：")
    print("\n1️⃣  确保将机器人添加为频道管理员：")
    print(f"   • 进入频道设置 → 管理员 → 添加管理员")
    print(f"   • 搜索您的机器人并添加")
    print(f"   • 至少给予「发布消息」权限")
    
    print("\n2️⃣  启动机器人：")
    print("   • Docker 方式：docker-compose up -d")
    print("   • 直接运行：  python3 main.py")
    print("   • 脚本启动：  ./start.sh")
    
    print("\n3️⃣  测试机器人：")
    print("   • 在 Telegram 中找到您的机器人")
    print("   • 发送 /start 命令")
    print("   • 发送 /help 查看所有命令")
    
    print("\n💡 提示：使用 python3 check_config.py 可以验证配置")
    print("\n")
    
    return True

def main():
    """主函数"""
    try:
        success = create_config()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ 配置已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 配置失败：{e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

