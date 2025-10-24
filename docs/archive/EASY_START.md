# 🚀 TeleSubmit v2 - 超简单部署指南

只需一个命令，3 分钟完成部署！

## 📦 一键快速启动

```bash
./quickstart.sh
```

就这么简单！脚本会自动：

1. ✅ **检测配置** - 如果是首次运行，自动启动配置向导
2. ✅ **检测环境** - 自动识别 Docker 或 Python 环境
3. ✅ **智能部署** - 选择最佳部署方式
4. ✅ **验证启动** - 确保机器人正常运行

---

## 🎯 完整流程演示

### 首次运行

```bash
cd TeleSubmit-v2

# 一键启动
./quickstart.sh
```

**脚本会引导您完成：**

```
╔════════════════════════════════════════════════════════════════╗
║           🤖 TeleSubmit v2 快速启动向导                       ║
╚════════════════════════════════════════════════════════════════╝

📋 步骤 1/3: 配置检查
────────────────────────────────────────────────────────────────
✨ 检测到这是首次运行！

🎯 准备启动配置向导...

配置向导将引导您完成以下配置：
  1️⃣  输入 Telegram Bot Token
  2️⃣  设置投稿频道 ID
  3️⃣  配置所有者 User ID
  4️⃣  选择可选功能（搜索、通知等）

按回车键开始配置...
```

**然后会进入交互式配置：**

1. 输入 Bot Token（从 @BotFather 获取）
2. 输入频道 ID（@频道名 或 -100xxx）
3. 输入您的 User ID（从 @userinfobot 获取）
4. 选择可选功能

**配置完成后自动启动！**

---

## 🎨 三种部署方式

### 方式 1️⃣ - 超级简单（推荐新手）

```bash
./quickstart.sh
```

一键完成所有操作，适合：
- 🆕 首次使用
- 🤷 不确定用什么方式
- 🚀 想要最快部署

---

### 方式 2️⃣ - Docker 部署（推荐生产环境）

```bash
# 自动配置 + Docker 部署
./deploy.sh

# 或手动配置后部署
python3 setup_wizard.py  # 配置
./deploy.sh              # 部署
```

优点：
- ✅ 环境隔离
- ✅ 易于管理
- ✅ 一键重启
- ✅ 适合服务器

---

### 方式 3️⃣ - 直接运行（推荐开发）

```bash
# 自动配置 + 直接运行
./start.sh

# 或手动配置后运行
python3 setup_wizard.py  # 配置
./start.sh              # 运行
```

优点：
- ✅ 快速调试
- ✅ 易于修改
- ✅ 适合开发

---

## 📋 前置准备

### 获取 Bot Token

1. 在 Telegram 找 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 按提示设置名称和用户名
4. 复制获得的 Token

### 创建频道并获取 ID

**公开频道：**
- 格式：`@频道用户名`（如 `@mychannel`）

**私有频道：**
- 将 [@userinfobot](https://t.me/userinfobot) 添加到频道
- 它会告诉你频道 ID（如 `-1001234567890`）

⚠️ **重要**：将机器人添加为频道管理员，给予「发布消息」权限

### 获取您的 User ID

1. 在 Telegram 找 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 复制返回的 ID（纯数字）

---

## ✅ 测试机器人

部署完成后，在 Telegram 中测试：

```
1. 找到您的机器人（搜索用户名）
2. 发送 /start  ← 应该收到欢迎消息
3. 发送 /help   ← 查看所有命令
4. 发送 /submit ← 测试投稿功能
```

---

## 🔧 常见问题

### Q: 配置向导卡住了怎么办？

按 `Ctrl+C` 退出，然后：

```bash
# 手动编辑配置
nano config.ini

# 验证配置
python3 check_config.py

# 重新启动
./quickstart.sh
```

### Q: 想修改配置怎么办？

```bash
# 方式 1: 重新运行配置向导
python3 setup_wizard.py

# 方式 2: 直接编辑配置文件
nano config.ini
```

### Q: 机器人无响应？

检查清单：

```bash
# 1. 查看日志
docker-compose logs -f  # Docker 部署
# 或直接查看控制台输出

# 2. 检查配置
python3 check_config.py

# 3. 验证 Token
# 确保 Token 正确且机器人已启用

# 4. 检查网络
# 确保能访问 Telegram API
```

### Q: 无法发送到频道？

确保：
- ✅ 机器人已添加为频道管理员
- ✅ 机器人有「发布消息」权限
- ✅ 频道 ID 格式正确

---

## 📊 管理命令

### Docker 部署

```bash
# 查看日志
docker-compose logs -f

# 重启机器人
docker-compose restart

# 停止机器人
docker-compose stop

# 启动机器人
docker-compose start

# 完全停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 直接运行

```bash
# 启动
./start.sh

# 停止
按 Ctrl+C

# 后台运行
nohup ./start.sh > logs/bot.log 2>&1 &

# 查看日志
tail -f logs/bot.log
```

---

## 🎉 大功告成！

现在您的投稿机器人已经运行了！

**功能特色：**
- 📝 投稿管理 - 文字、图片、视频、文档
- 🔍 全文搜索 - 支持中文分词
- 🏷️ 标签系统 - 自动标签云
- 📊 统计分析 - 热度排行
- 👤 用户系统 - 个人统计
- 🚫 黑名单 - 管理功能

**需要帮助？**
- 📖 查看 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - 详细部署文档
- 📖 查看 [README.md](README.md) - 完整功能说明
- 📖 查看 [QUICKSTART.md](QUICKSTART.md) - 快速入门

---

**祝您使用愉快！🎊**

有任何问题随时查看文档或运行 `python3 check_config.py` 诊断配置。

