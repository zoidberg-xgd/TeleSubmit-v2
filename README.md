# TeleSubmit v2

Telegram 频道投稿机器人，支持媒体上传、全文搜索、热度统计。

## 主要功能

- **投稿管理**：支持图片、视频、文档批量上传
- **全文搜索**：基于 Whoosh 的中文搜索引擎，支持**文件名搜索**
- **热度统计**：智能热度算法，支持排行榜
- **标签系统**：标签云可视化
- **黑名单管理**：用户权限控制

## 系统要求

- **内存**: 256 MB - 1 GB（取决于频道规模）
- **磁盘**: 100 MB 以上
- **Python**: 3.9+（推荐 3.11）



## 快速开始

### 部署方式

#### 方式一：快速启动向导（推荐）

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
./quickstart.sh
```

快速启动向导会：
- 自动检测系统环境（Python、Docker、Git）
- 智能推荐最适合的部署方式
- 一键部署简化操作流程

#### 方式二：一键安装（完整向导）

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
./install.sh
```

一键安装脚本会：
- 检测 Python 版本和依赖
- 自动安装所需包
- 交互式配置向导
- 初始化数据库
- 自动启动机器人

#### 方式三：Docker 部署（推荐生产环境）

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
cp config.ini.example config.ini
nano config.ini  # 填入必要配置
./deploy.sh
```

Docker 部署优势：
- 环境隔离：独立运行环境
- 自动重启：异常退出自动恢复
- 易于迁移：一键部署到任何服务器

#### 方式四：手动部署

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
pip3 install -r requirements.txt
cp config.ini.example config.ini
nano config.ini  # 填入必要配置
./start.sh
```

## 基本配置

编辑 `config.ini`，填入以下必填项：

```ini
[BOT]
TOKEN = your_bot_token_here        # 从 @BotFather 获取
CHANNEL_ID = @your_channel         # 频道用户名或 ID
OWNER_ID = 123456789               # 您的 Telegram User ID
```

获取方式：
- **Bot Token**：向 @BotFather 发送 `/newbot` 创建机器人
- **Channel ID**：频道用户名（如 @mychannel）或数字 ID
- **Owner ID**：向 @userinfobot 发送任意消息获取

详细配置请查看 [部署指南](DEPLOYMENT.md)。

## 脚本命令

### 首次部署

根据您的需求选择合适的方式：

```bash
# 方式 1: 一键安装（最简单）
./install.sh

# 方式 2: 快速启动向导（智能选择）
./quickstart.sh

# 方式 3: Docker 部署（推荐生产环境）
./deploy.sh
```

### 日常管理

```bash
# 启动和停止
./start.sh              # 启动机器人（后台运行）
./restart.sh            # 重启机器人
./restart.sh --stop     # 仅停止机器人

# 更新
./update.sh             # 拉取最新代码并重启
./upgrade.sh            # 功能升级（包含数据迁移）

# 卸载
./uninstall.sh          # 完全卸载（会先备份数据）
```

### 状态查看

```bash
# 查看进程
ps aux | grep "python.*main.py"

# 查看日志
tail -f logs/bot.log             # 标准日志
tail -f logs/error.log           # 错误日志

# Docker 状态（如果使用 Docker）
docker-compose ps                # 容器状态
docker-compose logs -f           # 容器日志
```

### 常用场景

| 场景 | 命令 |
|------|------|
| 首次安装 | `./install.sh` |
| 修改配置后 | `./restart.sh` |
| 更新版本 | `./update.sh` |
| 功能升级 | `./upgrade.sh` |
| Docker 重新部署 | `./deploy.sh --rebuild` |
| 查看运行日志 | `tail -f logs/bot.log` |

## 使用命令

### 用户命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用机器人 |
| `/submit` | 开始新投稿 |
| `/cancel` | 取消当前投稿 |
| `/help` | 查看帮助信息 |
| `/settings` | 查看机器人设置 |

### 搜索与统计

| 命令 | 说明 | 示例 |
|------|------|------|
| `/search <关键词>` | 搜索帖子（标题/简介/标签/文件名） | `/search Python教程` |
| `/search <文件名>` | 搜索文件名 | `/search 文件.txt` |
| `/hot [数量] [时间]` | 热门排行 | `/hot 20 week` |
| `/tags [数量]` | 标签云 | `/tags 50` |
| `/mystats` | 我的统计 | `/mystats` |
| `/myposts [数量]` | 我的投稿 | `/myposts 20` |

搜索范围：标题、简介、标签、**文件名**（新功能）  
时间参数：`day`（今日）、`week`（本周）、`month`（本月）、`all`（全部，默认）

### 管理员命令

| 命令 | 说明 |
|------|------|
| `/debug` | 系统状态 |
| `/blacklist_add <ID> [原因]` | 添加黑名单 |
| `/blacklist_remove <ID>` | 移除黑名单 |
| `/blacklist_list` | 查看黑名单 |
| `/searchuser <ID>` | 查询用户投稿 |

**删除帖子**：仅限 OWNER_ID 用户
- 删除功能通过回调按钮触发（非命令）
- 删除操作会清理：数据库记录、搜索索引；不会自动删除频道消息
- 详细说明请查看 [删除帖子指南](DELETE_POST_GUIDE.md)

详细管理功能请查看 [管理员指南](ADMIN_GUIDE.md)。

## 投稿流程

1. 发送 `/submit` 开始投稿
2. 选择类型（媒体/文档/混合）
3. 上传文件（媒体最多50个，文档最多10个）
4. 发送 `/done_media` 或 `/done_doc` 完成上传
5. 输入标签（必填，至少1个，最多30个）
6. 输入可选信息（链接、标题、说明）
7. 预览并确认
8. 发布到频道

## 搜索功能

基础搜索：
```
/search Python              # 搜索关键词
/search #编程               # 搜索标签
/search 文件.txt            # 搜索文件名
```

高级搜索：
```
/search Python -t week      # 限定时间范围
/search 教程 -n 20          # 限定结果数量
/search #Python -t month -n 15  # 组合使用
```

搜索特性：
- 中文分词优化（jieba）
- 多字段匹配（标题/描述/标签/文件名）
- 按相关度和热度排序
- 时间范围筛选
- 自动索引管理和同步

### 索引管理

系统自动管理搜索索引，支持以下功能：

- **自动重建**: 系统启动时检测索引状态，Schema 不匹配时自动重建
- **增量同步**: 定期同步数据库和索引，保持数据一致性
- **索引优化**: 自动优化索引结构，提升搜索性能
- **手动管理**: 参考 `utils/index_manager.py` 提供的管理能力

详细信息请查看 [索引管理器文档](INDEX_MANAGER_README.md)

## 项目结构

```
TeleSubmit-v2/
├── config/              # 配置管理
├── handlers/            # 消息处理器
│   ├── command_handlers.py
│   ├── submit_handlers.py
│   ├── search_handlers.py
│   ├── stats_handlers.py
│   ├── callback_handlers.py
│   └── publish.py
├── utils/               # 工具模块
│   ├── database.py
│   ├── search_engine.py
│   ├── index_manager.py
│   ├── heat_calculator.py
│   ├── blacklist.py
│   └── file_validator.py
├── ui/                  # 用户界面
│   ├── keyboards.py
│   └── messages.py
├── data/                # 数据目录
│   ├── submissions.db
│   ├── user_sessions.db
│   └── search_index/
├── logs/                # 日志目录
├── main.py              # 主程序入口
├── requirements.txt     # Python 依赖
├── config.ini.example   # 配置模板
├── docker-compose.yml   # Docker 编排文件
├── Dockerfile           # Docker 镜像构建
├── install.sh           # 一键安装
├── quickstart.sh        # 快速启动
├── deploy.sh            # Docker 部署
├── start.sh             # 启动脚本
├── restart.sh           # 重启脚本
├── update.sh            # 更新脚本
├── upgrade.sh           # 功能升级
└── uninstall.sh         # 卸载脚本
```

## 部署环境要求

**最低配置：**
- 操作系统：Linux / macOS / Windows (WSL2)
- Python：>= 3.9
- 内存：>= 256 MB
- 磁盘：>= 500 MB
- 网络：可访问 api.telegram.org

**推荐配置：**
- 操作系统：Ubuntu 22.04 LTS / Debian 12 / macOS
- Python：3.11+
- 内存：>= 512 MB
- 磁盘：>= 2 GB
- CPU：>= 1 核

**Docker 部署：**
- Docker：>= 20.10
- Docker Compose：>= 2.0
- 内存：>= 512 MB（容器限制）

## 文档

| 文档 | 说明 |
|------|------|
| [README](README.md) | 项目介绍、快速开始 |
| [脚本指南](SCRIPTS_GUIDE.md) | **所有管理脚本详细说明** |
| [部署指南](DEPLOYMENT.md) | 详细部署步骤、故障排查 |
| [管理员指南](ADMIN_GUIDE.md) | 管理功能、系统维护 |
| [索引管理器](INDEX_MANAGER_README.md) | 搜索索引管理工具 |
| [内存占用说明](MEMORY_USAGE.md) | 内存使用分析与优化 |
| [更新日志](CHANGELOG.md) | 版本历史、功能更新 |
| 文档导航（已合并到 README 与各专题文档） | — |

推荐阅读顺序：
1. 首次部署：README → 脚本指南 → 部署指南
2. 日常使用：README（命令部分）
3. 脚本使用：脚本指南（所有脚本详解）
4. 管理维护：管理员指南
5. 更新系统：运行 `./update.sh`

## 故障排查

**机器人无法启动？**
1. 检查配置文件：`python3 check_config.py`
2. 查看日志：`tail -f logs/bot.log`
3. 检查进程：`ps aux | grep python`

**搜索功能异常？**
1. 重建搜索索引：`python3 migrate_to_search.py`
2. 同步/查看索引状态：参考 `utils/index_manager.py` 或文档
3. 检查索引目录：`ls -la data/search_index/`

**热度数据不更新？**
- 热度每小时自动更新一次
- 手动触发：重启机器人即可

更多问题请查看 [部署指南](DEPLOYMENT.md) 的故障排查章节。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE)。

## 帮助与支持

- **问题反馈**：[GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues)
- **功能建议**：[GitHub Discussions](https://github.com/zoidberg-xgd/TeleSubmit-v2/discussions)
- **开发者**：[@zoidberg-xgd](https://github.com/zoidberg-xgd)

---

Made by [zoidberg-xgd](https://github.com/zoidberg-xgd)
