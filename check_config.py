#!/usr/bin/env python3
"""
配置检查脚本
用于验证 TeleSubmit v2 的配置是否正确
"""
import os
import sys

def check_python_version():
    """检查 Python 版本"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"❌ Python 版本过低: {major}.{minor}")
        print("   需要 Python 3.8 或更高版本")
        return False
    print(f"✅ Python 版本: {major}.{minor}")
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = {
        'telegram': 'python-telegram-bot',
        'aiosqlite': 'aiosqlite',
        'dotenv': 'python-dotenv',
    }
    
    all_ok = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
    
    return all_ok

def check_config_file():
    """检查配置文件"""
    if os.path.exists('config.ini'):
        print("✅ config.ini 存在")
        
        # 读取配置
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            # 检查必要配置
            if config.has_option('BOT', 'TOKEN'):
                token = config.get('BOT', 'TOKEN')
                if token and token != 'your_bot_token_here':
                    print("✅ TOKEN 已配置")
                else:
                    print("⚠️  TOKEN 未配置或使用默认值")
                    return False
            else:
                print("❌ config.ini 缺少 TOKEN")
                return False
            
            if config.has_option('BOT', 'CHANNEL_ID'):
                channel = config.get('BOT', 'CHANNEL_ID')
                if channel and channel != '@your_channel':
                    print("✅ CHANNEL_ID 已配置")
                else:
                    print("⚠️  CHANNEL_ID 未配置或使用默认值")
                    return False
            else:
                print("❌ config.ini 缺少 CHANNEL_ID")
                return False
            
            return True
        except Exception as e:
            print(f"❌ 读取 config.ini 失败: {e}")
            return False
    else:
        print("⚠️  config.ini 不存在，将尝试使用环境变量")
        return None

def check_env_vars():
    """检查环境变量"""
    token = os.getenv('TOKEN')
    channel = os.getenv('CHANNEL_ID')
    
    has_token = token is not None
    has_channel = channel is not None
    
    if has_token:
        print("✅ 环境变量 TOKEN 已设置")
    else:
        print("❌ 环境变量 TOKEN 未设置")
    
    if has_channel:
        print("✅ 环境变量 CHANNEL_ID 已设置")
    else:
        print("❌ 环境变量 CHANNEL_ID 未设置")
    
    return has_token and has_channel

def check_project_structure():
    """检查项目结构"""
    required_dirs = ['config', 'handlers', 'utils', 'models', 'database', 'ui']
    required_files = ['main.py', 'requirements.txt']
    
    all_ok = True
    
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✅ 目录 {dir_name}/ 存在")
        else:
            print(f"❌ 目录 {dir_name}/ 缺失")
            all_ok = False
    
    for file_name in required_files:
        if os.path.isfile(file_name):
            print(f"✅ 文件 {file_name} 存在")
        else:
            print(f"❌ 文件 {file_name} 缺失")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("=" * 60)
    print("TeleSubmit v2 配置检查")
    print("=" * 60)
    print()
    
    # 检查 Python 版本
    print("📌 检查 Python 版本...")
    python_ok = check_python_version()
    print()
    
    # 检查依赖
    print("📌 检查依赖包...")
    deps_ok = check_dependencies()
    print()
    
    # 检查项目结构
    print("📌 检查项目结构...")
    structure_ok = check_project_structure()
    print()
    
    # 检查配置
    print("📌 检查配置...")
    config_ok = check_config_file()
    
    if config_ok is None:
        # 配置文件不存在，检查环境变量
        env_ok = check_env_vars()
        config_ok = env_ok
    elif config_ok is False:
        # 配置文件存在但配置不完整，检查环境变量作为后备
        print("   检查环境变量作为后备...")
        env_ok = check_env_vars()
        if env_ok:
            config_ok = True
            print("✅ 可以使用环境变量配置")
    
    print()
    print("=" * 60)
    
    # 汇总结果
    if all([python_ok, deps_ok, structure_ok, config_ok]):
        print("✅ 所有检查通过！可以启动机器人了")
        print()
        print("启动命令:")
        print("  python3 main.py")
        print("  或")
        print("  ./start.sh")
        return 0
    else:
        print("❌ 检查失败，请修复以上问题")
        print()
        
        if not python_ok:
            print("💡 升级 Python:")
            print("   brew install python@3.11  # macOS")
            print("   sudo apt install python3.11  # Ubuntu")
        
        if not deps_ok:
            print("💡 安装依赖:")
            print("   pip3 install -r requirements.txt")
        
        if not config_ok:
            print("💡 配置机器人:")
            print("   方法 1: 复制并编辑配置文件")
            print("     cp config.ini.example config.ini")
            print("     nano config.ini")
            print()
            print("   方法 2: 设置环境变量")
            print("     export TOKEN='your_token'")
            print("     export CHANNEL_ID='@your_channel'")
        
        return 1

if __name__ == '__main__':
    sys.exit(main())

