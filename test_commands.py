#!/usr/bin/env python3
"""测试机器人命令菜单"""
import asyncio
import sys
from telegram import Bot
from config.settings import TOKEN

async def test_commands():
    if not TOKEN:
        print("❌ 未配置 Bot Token，请先运行: python3 setup_wizard.py")
        sys.exit(1)
    
    try:
        bot = Bot(token=TOKEN)
        commands = await bot.get_my_commands()
        
        if not commands:
            print("⚠️  命令菜单未设置，启动机器人后自动配置")
        else:
            print(f"✅ 已设置 {len(commands)} 个命令：\n")
            for cmd in commands:
                print(f"  /{cmd.command:<12} {cmd.description}")
            print(f"\n💡 用户在 Telegram 中点击 / 按钮即可看到命令列表")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(test_commands())
    except KeyboardInterrupt:
        print("\n已取消")

