<div align="center">

# 🤖 TeleSubmit v2

**功能强大的 Telegram 频道投稿机器人**

一站式投稿管理解决方案，支持媒体上传、全文搜索、热度统计

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab.svg?logo=python&logoColor=white)](https://www.python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26a5e4.svg?logo=telegram&logoColor=white)](https://telegram.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg?logo=docker&logoColor=white)](https://www.docker.com)

[🚀 快速开始](#-快速开始) • [📖 文档](#-完整文档) • [✨ 功能](#-核心功能) • [🐛 反馈](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues)

</div>

---

## 🌟 项目亮点

<table>
<tr>
<td width="50%">

### 💡 智能投稿系统
- ✅ 支持图片、视频、文档多种类型
- ✅ 批量上传（媒体50个、文档10个）
- ✅ 智能文件类型过滤
- ✅ 标签系统与标签云可视化
- ✅ 会话管理，随时可取消

</td>
<td width="50%">

### 🔍 强大搜索引擎
- ✅ 基于 Whoosh 的全文搜索
- ✅ 中文分词（jieba）优化
- ✅ 多字段智能匹配
- ✅ 按相关度和热度排序
- ✅ 时间范围筛选

</td>
</tr>
<tr>
<td>

### 📊 热度统计分析
- ✅ 智能热度算法（浏览+转发+反应）
- ✅ 时间衰减机制（7天半衰期）
- ✅ 热门排行榜
- ✅ 个人投稿统计

</td>
<td>

### 🛡️ 完善管理功能
- ✅ 黑名单系统
- ✅ 用户投稿查询
- ✅ 系统状态监控
- ✅ 权限精细控制

</td>
</tr>
</table>

---

## 🚀 快速开始

### 方式一：一键安装（强烈推荐）

```bash
# 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 一键安装并部署
chmod +x install.sh
./install.sh
```

**安装脚本会自动：**
- 🔍 检测系统环境
- 📦 安装必要依赖
- ⚙️ 引导完成配置
- 🚀 启动机器人服务

### 方式二：Docker 部署

```bash
# 1. 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 2. 配置
cp config.ini.example config.ini
nano config.ini  # 填入 Token、频道ID、所有者ID

# 3. 一键部署
chmod +x deploy.sh
./deploy.sh

# 查看日志
docker-compose logs -f
```

### 方式三：直接运行

```bash
# 1. 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 配置
cp config.ini.example config.ini
nano config.ini

# 4. 启动
chmod +x start.sh
./start.sh
```

---

## 📋 前置准备

### 1️⃣ 获取 Bot Token

1. 在 Telegram 找 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称，获取 Token

### 2️⃣ 准备频道

1. 创建一个 Telegram 频道
2. 将机器人添加为管理员
3. 给予「发布消息」权限
4. 获取频道 ID：
   - 公开频道：`@channel_username`
   - 私有频道：转发频道消息给 [@userinfobot](https://t.me/userinfobot) 获取 ID

### 3️⃣ 获取您的 User ID

1. 在 Telegram 找 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 获取显示的 User ID 数字

---

## ⚙️ 配置说明

### 最小配置

编辑 `config.ini`，填入以下三个必填项即可：

```ini
[Telegram]
TOKEN = your_bot_token_here        # 机器人 Token
CHANNEL_ID = @your_channel         # 频道 ID
OWNER_ID = 123456789               # 您的 User ID
```

### 完整配置示例

```ini
[Telegram]
# === 必填项 ===
TOKEN = 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_ID = @your_channel
OWNER_ID = 123456789

# === 可选项 ===
ADMIN_IDS = 111111111,222222222    # 管理员ID（逗号分隔）

[Bot]
BOT_MODE = MIXED                    # 模式：MIXED/SUBMISSION_ONLY/SEARCH_ONLY
SHOW_SUBMITTER = yes               # 是否显示投稿者信息
ENABLE_NOTIFICATIONS = yes         # 是否启用新投稿通知
ALLOWED_TAGS = 30                  # 最大标签数量
SESSION_TIMEOUT = 300              # 会话超时时间（秒）

[Media]
MEDIA_VALIDATION = strict          # 媒体验证：strict/basic/none
ALLOWED_FILE_TYPES = *             # 允许的文件类型（* 表示全部）

[Search]
ENABLE_SEARCH = yes                # 是否启用搜索功能
MAX_SEARCH_RESULTS = 50            # 最大搜索结果数
INDEX_DIR = data/search_index      # 搜索索引目录

[Database]
DB_PATH = data/submissions.db      # 数据库路径
```

### 🎯 文件类型过滤示例

根据频道用途自定义允许的文件类型：

```ini
# 📚 小说/电子书频道
ALLOWED_FILE_TYPES = .txt,.epub,.mobi,.pdf,.azw3

# 🎮 游戏频道
ALLOWED_FILE_TYPES = .zip,.rar,.7z,.apk,.exe

# 🎵 音乐频道
ALLOWED_FILE_TYPES = .mp3,.flac,.wav,.aac,.m4a,.ogg

# 🎬 视频频道
ALLOWED_FILE_TYPES = .mp4,.mkv,.avi,.mov,.wmv

# 📄 办公文档
ALLOWED_FILE_TYPES = .pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx

# 🔓 允许所有类型（默认）
ALLOWED_FILE_TYPES = *
```

**高级配置：**

```ini
# 使用 MIME 类型
ALLOWED_FILE_TYPES = application/pdf,application/zip

# 使用通配符（所有音频和视频）
ALLOWED_FILE_TYPES = audio/*,video/*

# 混合使用（扩展名 + MIME 类型）
ALLOWED_FILE_TYPES = .pdf,.zip,audio/*,video/*
```

### 🔍 配置检查工具

```bash
# 检查配置是否正确
python3 check_config.py

# 使用配置向导（交互式）
python3 setup_wizard.py
```

---

## 📱 使用命令

### 👥 用户命令

<table>
<tr>
<th width="30%">命令</th>
<th width="70%">说明</th>
</tr>
<tr>
<td><code>/start</code></td>
<td>🚀 开始使用机器人，显示欢迎信息</td>
</tr>
<tr>
<td><code>/submit</code></td>
<td>📝 开始新投稿流程</td>
</tr>
<tr>
<td><code>/cancel</code></td>
<td>❌ 取消当前投稿</td>
</tr>
<tr>
<td><code>/help</code></td>
<td>❓ 查看帮助信息和命令列表</td>
</tr>
<tr>
<td><code>/settings</code></td>
<td>⚙️ 查看机器人设置和功能</td>
</tr>
</table>

### 🔍 搜索与统计

<table>
<tr>
<th width="30%">命令</th>
<th width="40%">说明</th>
<th width="30%">示例</th>
</tr>
<tr>
<td><code>/search &lt;关键词&gt;</code></td>
<td>搜索帖子内容</td>
<td><code>/search Python教程</code></td>
</tr>
<tr>
<td><code>/hot [数量] [时间]</code></td>
<td>查看热门帖子排行</td>
<td><code>/hot 20 week</code></td>
</tr>
<tr>
<td><code>/tags [数量]</code></td>
<td>查看标签云</td>
<td><code>/tags 50</code></td>
</tr>
<tr>
<td><code>/mystats</code></td>
<td>查看我的投稿统计</td>
<td><code>/mystats</code></td>
</tr>
<tr>
<td><code>/myposts [数量]</code></td>
<td>查看我的投稿列表</td>
<td><code>/myposts 20</code></td>
</tr>
</table>

**时间范围参数：**
- `day` - 今日
- `week` - 本周
- `month` - 本月
- `all` - 全部（默认）

### 👑 管理员命令

<table>
<tr>
<th width="40%">命令</th>
<th width="60%">说明</th>
</tr>
<tr>
<td><code>/debug</code></td>
<td>📊 查看系统状态和资源使用情况</td>
</tr>
<tr>
<td><code>/blacklist_add &lt;ID&gt; [原因]</code></td>
<td>🚫 将用户加入黑名单</td>
</tr>
<tr>
<td><code>/blacklist_remove &lt;ID&gt;</code></td>
<td>✅ 将用户移出黑名单</td>
</tr>
<tr>
<td><code>/blacklist_list</code></td>
<td>📋 查看黑名单列表</td>
</tr>
<tr>
<td><code>/searchuser &lt;ID&gt;</code></td>
<td>🔍 查询指定用户的投稿记录</td>
</tr>
</table>

> 📘 详细管理功能请查看 [管理员指南](ADMIN_GUIDE.md)

---

## ✨ 核心功能

### 📝 投稿流程

```
1️⃣  发送 /submit
2️⃣  选择投稿类型（媒体/文档/混合）
3️⃣  上传文件
     • 媒体：最多 50 个（图片/视频）
     • 文档：最多 10 个
4️⃣  发送 /done_media 或 /done_doc 完成上传
5️⃣  输入标签（空格或逗号分隔，最多30个）
6️⃣  输入可选信息：
     • 链接（支持多个，用空格分隔）
     • 标题
     • 说明
     • 剧透标记
7️⃣  预览并确认
8️⃣  发布到频道 ✅
```

### 🔍 搜索功能

**基础搜索：**
```
/search Python              # 搜索关键词
/search #编程               # 搜索标签
```

**高级搜索：**
```
/search Python -t week      # 限定时间范围
/search 教程 -n 20          # 限定结果数量
/search #Python -t month -n 15  # 组合使用
```

**搜索引擎特性：**
- 🔤 中文分词优化（jieba）
- 🎯 多字段智能匹配（标题/描述/标签）
- 📊 按相关度和热度排序
- ⏰ 时间范围筛选
- 💡 高亮显示匹配结果

### 📊 热度算法

**计算公式：**

```
热度分数 = (浏览数 × 0.3 + 转发数 × 10 × 0.4 + 反应数 × 5 × 0.3) × 时间衰减因子
```

**时间衰减机制：**
- 📉 半衰期：7 天
- 🧮 公式：`2^(-天数/7)`
- 🎯 效果：新内容权重更高，旧内容逐渐降低

**更新策略：**
- ⏰ 每小时自动更新最近 30 天的帖子
- ⚡ 平衡准确性与 API 请求频率

### 🏷️ 标签系统

**功能特性：**
- ✅ 必填项，至少 1 个标签
- ✅ 最多 30 个标签（可配置）
- ✅ 自动去重和格式化
- ✅ 支持 `#标签` 和 `标签` 两种格式
- ✅ 标签云可视化展示（按使用频率）

**标签云示例：**
```
/tags 50

📊 标签云（Top 50）

#Python (125)  #编程 (98)  #教程 (87)
#JavaScript (76)  #Web开发 (65)  ...
```

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 完全删除（保留数据）
docker-compose down

# 完全删除（删除数据卷）
docker-compose down -v

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 使用 Makefile

```bash
# 查看所有命令
make help

# 一键部署
make deploy

# 查看日志
make logs

# 重启
make restart

# 备份数据
make backup

# 进入容器
make shell

# 运行迁移
make migrate

# 更新到最新版本
make update
```

### 数据持久化

Docker 已自动挂载以下目录：
- `./config.ini` → `/app/config.ini`
- `./data/` → `/app/data/`
- `./logs/` → `/app/logs/`

容器重启不会丢失数据。

---

## 🔄 更新和维护

### 更新到最新版本

**自动更新（推荐）：**

```bash
chmod +x update.sh
./update.sh
```

更新脚本会自动：
- 📦 备份当前数据和配置
- ⬇️ 拉取最新代码
- 🔨 重新构建并重启服务
- 📊 显示更新日志

**手动更新：**

```bash
# 备份数据
cp -r data data_backup_$(date +%Y%m%d)

# 拉取代码
git pull

# Docker 部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 直接运行
pip3 install -r requirements.txt --upgrade
# 重启应用
```

### 数据备份

```bash
# 使用 Makefile
make backup

# 手动备份
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    config.ini data/ logs/
```

### 卸载

```bash
# 使用卸载脚本
chmod +x uninstall.sh
./uninstall.sh

# 手动卸载 Docker
docker-compose down -v
docker rmi telesubmit-v2

# 手动卸载 Systemd
sudo systemctl stop telesubmit
sudo systemctl disable telesubmit
sudo rm /etc/systemd/system/telesubmit.service
```

---

## 📖 完整文档

<table>
<tr>
<th width="30%">文档</th>
<th width="50%">说明</th>
<th width="20%">适用人群</th>
</tr>
<tr>
<td>📘 <a href="README.md">README</a></td>
<td>项目介绍、快速开始、核心功能</td>
<td>⭐⭐⭐⭐⭐ 所有用户</td>
</tr>
<tr>
<td>🚀 <a href="DEPLOYMENT.md">部署指南</a></td>
<td>详细部署步骤、多种部署方式、故障排查</td>
<td>⭐⭐⭐⭐ 部署人员</td>
</tr>
<tr>
<td>👑 <a href="ADMIN_GUIDE.md">管理员指南</a></td>
<td>管理功能、系统维护、数据管理</td>
<td>⭐⭐⭐ 管理员</td>
</tr>
<tr>
<td>📝 <a href="CHANGELOG.md">更新日志</a></td>
<td>版本历史、功能更新、问题修复</td>
<td>⭐⭐ 开发者</td>
</tr>
</table>

### 📚 推荐阅读顺序

1. **首次部署**：README → 部署指南
2. **日常使用**：README（命令部分）
3. **管理维护**：管理员指南
4. **深入了解**：`docs/archive/` 技术文档

---

## 🛠️ 故障排查

### ❌ 机器人无响应

**1. 检查配置**
```bash
python3 check_config.py
```

**2. 查看日志**
```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u telesubmit -n 50

# 直接运行
tail -f logs/error.log
```

**3. 验证网络**
```bash
ping api.telegram.org
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### ❌ 无法发送到频道

检查清单：
- ✅ 机器人是频道管理员
- ✅ 有「发布消息」权限
- ✅ 频道 ID 格式正确
  - 公开频道：`@channel_username`
  - 私有频道：`-100xxxxxxxxxx`

### ❌ 搜索功能不工作

重建搜索索引：
```bash
# 直接运行
python3 migrate_to_search.py

# Docker
docker exec telesubmit-v2 python migrate_to_search.py
```

### ❌ 权限错误

修复文件权限：
```bash
chmod -R 755 data/ logs/
chown -R $USER:$USER data/ logs/
```

> 📘 更多问题请查看 [部署指南](DEPLOYMENT.md) 故障排查章节

---

## 📂 项目结构

```
TeleSubmit-v2/
├── 📁 config/                   # 配置管理
│   └── settings.py             # 配置加载器
├── 📁 handlers/                 # 消息处理器
│   ├── command_handlers.py     # 基础命令
│   ├── submit_handlers.py      # 投稿流程
│   ├── search_handlers.py      # 搜索功能
│   ├── stats_handlers.py       # 统计功能
│   ├── callback_handlers.py    # 回调处理
│   └── publish.py              # 发布逻辑
├── 📁 utils/                    # 工具模块
│   ├── database.py             # 数据库操作
│   ├── search_engine.py        # 搜索引擎
│   ├── heat_calculator.py      # 热度计算
│   ├── blacklist.py            # 黑名单管理
│   └── file_validator.py       # 文件验证
├── 📁 ui/                       # 用户界面
│   ├── keyboards.py            # 键盘布局
│   └── messages.py             # 消息模板
├── 📁 data/                     # 数据目录
│   ├── submissions.db          # 主数据库
│   ├── user_sessions.db        # 会话数据
│   └── search_index/           # 搜索索引
├── 📁 logs/                     # 日志目录
├── 📄 main.py                   # 主程序入口
├── 🔧 setup_wizard.py           # 配置向导
├── 🔧 check_config.py           # 配置检查
├── 🔧 migrate_to_search.py      # 搜索迁移
├── 🚀 install.sh                # 一键安装脚本
├── 🚀 deploy.sh                 # Docker 部署脚本
├── 🚀 update.sh                 # 更新脚本
├── 🚀 start.sh                  # 启动脚本
├── 📋 requirements.txt          # Python 依赖
├── 🐳 Dockerfile                # Docker 镜像
├── 🐳 docker-compose.yml        # Docker Compose 配置
└── 📖 README.md                 # 项目文档
```

---

## 🔐 安全建议

1. **保护配置文件**
   ```bash
   chmod 600 config.ini
   ```

2. **使用环境变量**（可选）
   ```bash
   export TOKEN="your_bot_token"
   export CHANNEL_ID="@your_channel"
   export OWNER_ID="123456789"
   ```

3. **定期备份数据**
   ```bash
   # 添加到 crontab
   0 2 * * * cd /path/to/TeleSubmit-v2 && make backup
   ```

4. **更新依赖包**
   ```bash
   pip3 install -r requirements.txt --upgrade
   ```

5. **监控日志**
   ```bash
   # 设置日志轮转
   logrotate /etc/logrotate.d/telesubmit
   ```

---

## 📊 系统要求

### 最低配置

| 项目 | 要求 |
|------|------|
| **操作系统** | Linux / macOS / Windows (WSL2) |
| **Python** | >= 3.10 |
| **内存** | >= 512 MB |
| **磁盘** | >= 1 GB |
| **网络** | 可访问 api.telegram.org |

### 推荐配置

| 项目 | 推荐 |
|------|------|
| **操作系统** | Ubuntu 22.04 LTS / Debian 12 |
| **Python** | 3.11+ |
| **内存** | >= 1 GB |
| **磁盘** | >= 5 GB |
| **CPU** | >= 2 核 |

---

## 📦 依赖项

```txt
python-telegram-bot >= 20.0    # Telegram Bot API 框架
whoosh >= 2.7.4                # 全文搜索引擎
jieba >= 0.42.1                # 中文分词
Pillow >= 10.0.0               # 图像处理
psutil >= 5.9.0                # 系统监控
```

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

您可以自由地：
- ✅ 使用
- ✅ 复制
- ✅ 修改
- ✅ 合并
- ✅ 发布
- ✅ 分发
- ✅ 再许可
- ✅ 出售

---

## 💬 获取帮助

<table>
<tr>
<td width="25%">

### 🐛 问题反馈
[GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues)

</td>
<td width="25%">

### 💡 功能建议
[GitHub Discussions](https://github.com/zoidberg-xgd/TeleSubmit-v2/discussions)

</td>
<td width="25%">

### 👨‍💻 开发者
[@zoidberg-xgd](https://github.com/zoidberg-xgd)

</td>
<td width="25%">

### 📖 文档
[完整文档](https://github.com/zoidberg-xgd/TeleSubmit-v2)

</td>
</tr>
</table>

---

## 🎯 使用示例

### 📝 投稿示例

```
👤 用户: /submit
🤖 机器人: 请选择投稿类型...

👤 用户: [选择"媒体投稿"]
🤖 机器人: 请上传媒体文件...

👤 用户: [上传3张图片]
👤 用户: /done_media

🤖 机器人: 请输入标签...
👤 用户: Python 编程 教程

🤖 机器人: 请输入链接（可选）...
👤 用户: https://example.com

🤖 机器人: 预览如下，确认发布？
👤 用户: [点击"确认发布"]

✅ 发布成功！
```

### 🔍 搜索示例

```bash
# 搜索 Python 相关内容
/search Python

# 搜索本周的 Python 教程
/search Python教程 -t week

# 搜索最近 20 个编程相关内容
/search 编程 -n 20
```

### 📊 统计示例

```bash
# 查看本周热门 Top 10
/hot 10 week

# 查看我的投稿统计
/mystats

# 查看标签云 Top 30
/tags 30
```

---

## 🌟 致谢

感谢以下开源项目：

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API 框架
- [Whoosh](https://github.com/mchaput/whoosh) - 纯 Python 搜索引擎
- [jieba](https://github.com/fxsjy/jieba) - 中文分词库

---

<div align="center">

### 🎉 开始使用吧！

**如遇问题，请先运行 `python3 check_config.py` 诊断配置**

Made with ❤️ by [zoidberg-xgd](https://github.com/zoidberg-xgd)

⭐ 如果这个项目对您有帮助，请给个 Star！

[⬆ 回到顶部](#-telesubmit-v2)

</div>
