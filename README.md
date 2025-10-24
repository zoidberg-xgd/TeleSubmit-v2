# TeleSubmit v2 - Telegram 频道投稿机器人

一个功能完整的 Telegram 频道投稿助手，支持媒体/文档上传、全文搜索、热度统计等功能。

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ 主要功能

### 📝 投稿管理
- **多种内容类型**：图片、视频、文档、文字
- **批量上传**：媒体最多50个，文档最多10个
- **文件类型过滤**：可配置允许的文件类型，适应不同频道需求
- **标签系统**：必填标签，最多30个，支持标签云展示
- **可选信息**：链接、标题、说明、剧透标记
- **会话管理**：自动清理过期会话，可随时取消

### 🔍 搜索功能
- **全文搜索**：基于 Whoosh 引擎，支持中文分词（jieba）
- **多字段搜索**：标题、描述、标签智能匹配
- **结果排序**：按相关度和热度排序
- **时间筛选**：支持查询今日/本周/本月内容

### 📊 统计分析
- **热度算法**：综合浏览量、转发数、反应数计算
- **时间衰减**：7天半衰期，保证新鲜度
- **热门排行**：查看不同时间范围的热门内容
- **个人统计**：我的投稿列表和详细统计

### 👑 管理功能
- **黑名单系统**：封禁/解封用户
- **用户查询**：查看指定用户的投稿记录
- **系统调试**：资源使用、运行状态监控
- **权限控制**：管理员专属命令

---

## 🚀 快速开始

### 前置准备

1. **获取 Bot Token**
   - 在 Telegram 找 [@BotFather](https://t.me/BotFather)
   - 发送 `/newbot` 创建机器人
   - 复制获得的 Token

2. **创建频道**
   - 创建一个 Telegram 频道
   - 将机器人添加为管理员，给予「发布消息」权限
   - 获取频道 ID（公开频道用 `@频道名`，私有频道用数字 ID）

3. **获取您的 User ID**
   - 在 Telegram 找 [@userinfobot](https://t.me/userinfobot)
   - 发送任意消息获取您的 User ID

### 部署方式一：Docker（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit.git
cd TeleSubmit

# 2. 配置文件
cp config.ini.example config.ini
nano config.ini  # 填入 Token、频道ID、User ID

# 3. 启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 部署方式二：直接运行

```bash
# 1. 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit.git
cd TeleSubmit

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置文件
cp config.ini.example config.ini
nano config.ini  # 填入 Token、频道ID、User ID

# 4. 启动
python main.py

# 或后台运行
nohup python main.py > logs/bot.log 2>&1 &
```

---

## ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[BOT]
# === 必填项 ===
TOKEN = your_bot_token_here
CHANNEL_ID = @your_channel
OWNER_ID = your_user_id

# === 可选项 ===
# 数据库文件路径
DB_PATH = data/submissions.db

# 会话超时时间（秒）
TIMEOUT = 300

# 最大允许标签数
ALLOWED_TAGS = 30

# 机器人模式：MEDIA(仅图片视频) / DOCUMENT(仅文档) / MIXED(全部)
BOT_MODE = MIXED

# 是否在频道显示投稿人信息 (true/false)
SHOW_SUBMITTER = true

# 是否通知所有者新投稿 (true/false)
NOTIFY_OWNER = true

# 允许的文件类型（仅对文档模式生效）
# * = 允许所有类型（默认）
# 扩展名：.pdf,.zip,.txt
# MIME类型：application/pdf,application/zip
# 混合：.pdf,application/zip
# 通配符：audio/*,video/*
ALLOWED_FILE_TYPES = *

[SEARCH]
# 搜索索引目录
INDEX_DIR = data/search_index

# 是否启用搜索功能
ENABLED = true
```

**配置检查**：
```bash
python check_config.py
```

### 📂 文件类型过滤配置

根据频道用途，限制允许上传的文件类型：

```ini
# 小说频道
ALLOWED_FILE_TYPES = .txt,.epub,.mobi,.pdf,.doc,.docx

# 游戏频道
ALLOWED_FILE_TYPES = .zip,.rar,.7z,.apk,.exe

# 音乐频道
ALLOWED_FILE_TYPES = .mp3,.flac,.wav,.aac,.m4a

# 视频频道
ALLOWED_FILE_TYPES = .mp4,.mkv,.avi,.mov

# 办公文档
ALLOWED_FILE_TYPES = .pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx

# 允许所有类型（默认）
ALLOWED_FILE_TYPES = *
```

**高级配置**：
```ini
# 使用 MIME 类型
ALLOWED_FILE_TYPES = application/pdf,application/zip

# 使用 MIME 通配符（允许所有音频和视频）
ALLOWED_FILE_TYPES = audio/*,video/*

# 混合配置（扩展名 + MIME类型）
ALLOWED_FILE_TYPES = .pdf,.zip,application/vnd.android.package-archive
```

**用户体验**：
- ✅ 上传允许的文件 → 正常接收
- ❌ 上传不允许的文件 → 拒绝并提示用户允许的类型

---

## 📱 使用命令

### 基础命令（所有用户）

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用机器人 |
| `/submit` | 开始新投稿 |
| `/cancel` | 取消当前投稿 |
| `/help` | 查看帮助信息 |
| `/settings` | 查看机器人设置 |

### 统计与搜索

| 命令 | 说明 | 示例 |
|------|------|------|
| `/hot [数量] [时间]` | 查看热门帖子 | `/hot 20 week` |
| `/search <关键词>` | 搜索帖子 | `/search Python` |
| `/tags [数量]` | 查看标签云 | `/tags 50` |
| `/mystats` | 我的投稿统计 | `/mystats` |
| `/myposts [数量]` | 我的投稿列表 | `/myposts 20` |

**时间范围**：`day`（今日）、`week`（本周）、`month`（本月）

### 管理员命令（仅所有者）

| 命令 | 说明 |
|------|------|
| `/debug` | 查看系统调试信息 |
| `/blacklist_add <ID> [原因]` | 添加黑名单 |
| `/blacklist_remove <ID>` | 移除黑名单 |
| `/blacklist_list` | 查看黑名单列表 |
| `/searchuser <ID>` | 查询用户投稿 |

详细管理说明请查看 [ADMIN_GUIDE.md](ADMIN_GUIDE.md)

---

## 📂 项目结构

```
TeleSubmit-v2/
├── config/                  # 配置管理
│   └── settings.py
├── handlers/                # 消息处理器
│   ├── command_handlers.py # 命令处理
│   ├── submission_handlers.py # 投稿流程
│   ├── admin_handlers.py   # 管理功能
│   ├── search_handlers.py  # 搜索功能
│   ├── callback_handlers.py # 回调处理
│   └── publish.py          # 发布处理
├── utils/                   # 工具函数
│   ├── database.py         # 数据库操作
│   ├── search_engine.py    # 全文搜索引擎
│   ├── helpers.py          # 辅助函数
│   └── blacklist.py        # 黑名单管理
├── ui/                      # 用户界面
│   ├── keyboards.py        # 键盘布局
│   └── messages.py         # 消息模板
├── data/                    # 数据目录
│   ├── submissions.db      # SQLite 数据库
│   └── search_index/       # 搜索索引
├── logs/                    # 日志目录
├── main.py                  # 主程序
├── check_config.py          # 配置检查工具
├── migrate_to_search.py     # 搜索迁移工具
├── config.ini.example       # 配置示例
├── docker-compose.yml       # Docker 配置
├── Dockerfile               # Docker 镜像
└── requirements.txt         # Python 依赖
```

---

## 🔧 热度算法

热度分数 = `(浏览数 × 0.3 + 转发数 × 10 × 0.4 + 反应数 × 5 × 0.3) × 时间衰减因子`

**时间衰减**：
- 半衰期：7天
- 公式：`2^(-天数/7)`
- 效果：新帖子权重更高，旧帖子逐渐降低

**更新机制**：
- 自动每小时更新最近30天的帖子统计
- 平衡数据准确性和 API 请求频率

---

## 🐳 Docker 管理

### 常用命令

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart

# 停止
docker-compose stop

# 完全停止并删除
docker-compose down

# 重新构建
docker-compose up -d --build
```

### 数据持久化

Docker 配置已自动挂载以下目录：
- `./data` - 数据库和搜索索引
- `./logs` - 日志文件

数据会保存在宿主机，容器重启不会丢失。

---

## 🔍 搜索迁移

如果升级到 v2 版本，需要迁移现有数据到搜索索引：

```bash
# 直接运行
python migrate_to_search.py

# Docker 环境
docker-compose exec telesubmit-v2 python migrate_to_search.py
```

迁移工具会自动：
- 扫描数据库中的所有已发布帖子
- 建立全文搜索索引
- 支持增量更新

---

## 📖 文档导航

### 核心文档

| 文档 | 说明 | 适用人群 |
|------|------|----------|
| **[README.md](README.md)** | 项目介绍、快速开始、功能说明 | 所有用户 ⭐⭐⭐⭐⭐ |
| **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** | 详细部署步骤、故障排查 | 部署人员 ⭐⭐⭐⭐ |
| **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** | 管理员功能、系统维护 | 管理员 ⭐⭐⭐ |
| **[CHANGELOG.md](CHANGELOG.md)** | 版本历史、更新记录 | 开发者 ⭐⭐ |

### 推荐阅读顺序

1. **首次部署**：README.md → DEPLOY_GUIDE.md
2. **日常使用**：README.md（命令部分）
3. **管理维护**：ADMIN_GUIDE.md
4. **技术细节**：`docs/archive/` 目录下的技术文档

---

## 🛠️ 故障排查

### 机器人无响应

1. **检查配置**
   ```bash
   python check_config.py
   ```

2. **查看日志**
   ```bash
   # Docker
   docker-compose logs -f
   
   # 直接运行
   tail -f logs/bot.log
   ```

3. **验证网络**
   确保能访问 `api.telegram.org`

### 无法发送到频道

- ✅ 确认机器人是频道管理员
- ✅ 确认有「发布消息」权限
- ✅ 确认频道 ID 格式正确

### 搜索功能不工作

```bash
# 重建搜索索引
python migrate_to_search.py
```

更多问题请查看 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) 的故障排查章节。

---

## 📋 依赖项

```
python-telegram-bot >= 21.0  # Telegram Bot API
aiosqlite >= 0.17.0          # 异步 SQLite
whoosh >= 2.7.4              # 全文搜索引擎
jieba >= 0.42.1              # 中文分词
psutil >= 5.9.0              # 系统信息
configparser >= 6.0.0        # 配置解析
python-dotenv >= 1.0.0       # 环境变量
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 💬 支持

- **问题反馈**：[GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit/issues)
- **开发者**：[@zoidberg-xgd](https://github.com/zoidberg-xgd)
- **项目地址**：https://github.com/zoidberg-xgd/TeleSubmit

---

## 🎯 使用示例

### 投稿流程

```
1. 用户发送 /submit
2. 选择投稿类型（媒体/文档）
3. 上传文件
4. 发送 /done_media 或 /done_doc
5. 输入标签（用空格或逗号分隔）
6. 输入链接（可选，/skip_optional 跳过）
7. 输入标题（可选）
8. 输入说明（可选）
9. 选择是否设置剧透
10. 确认并发布
```

### 搜索示例

```
# 基础搜索
/search Python

# 搜索标签
/search #编程

# 限定时间范围
/search 教程 -t week

# 限定结果数量
/search Python -n 20

# 组合使用
/search #Python -t month -n 15
```

### 热门榜单

```
# 默认：前10个热门
/hot

# 查看前20个
/hot 20

# 查看本周前10个
/hot 10 week

# 查看本月前50个
/hot 50 month
```

---

<div align="center">

**🎉 开始使用吧！**

如有问题，请先运行 `python check_config.py` 诊断配置。

Made with ❤️ by [zoidberg-xgd](https://github.com/zoidberg-xgd)

</div>
