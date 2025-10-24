# TeleSubmit v2

Telegram 频道投稿机器人，支持媒体上传、全文搜索、热度统计。

## 主要功能

- **投稿管理**：支持图片、视频、文档批量上传
- **全文搜索**：基于 Whoosh 的中文搜索引擎
- **热度统计**：智能热度算法，支持排行榜
- **标签系统**：标签云可视化
- **黑名单管理**：用户权限控制

## 快速开始

### 方式一：一键安装（推荐）

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
chmod +x install.sh
./install.sh
```

安装脚本会自动检测环境、安装依赖、引导配置、启动服务。

### 方式二：Docker 部署

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
cp config.ini.example config.ini
nano config.ini  # 填入必要配置
chmod +x deploy.sh
./deploy.sh
```

### 方式三：直接运行

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
pip3 install -r requirements.txt
cp config.ini.example config.ini
nano config.ini  # 填入必要配置
chmod +x start.sh
./start.sh
```

## 基本配置

编辑 `config.ini`，填入以下必填项：

```ini
[Telegram]
TOKEN = your_bot_token_here        # 从 @BotFather 获取
CHANNEL_ID = @your_channel         # 频道用户名或 ID
OWNER_ID = 123456789               # 您的 Telegram User ID
```

获取方式：
- **Bot Token**：向 @BotFather 发送 `/newbot` 创建机器人
- **Channel ID**：频道用户名（如 @mychannel）或数字 ID
- **Owner ID**：向 @userinfobot 发送任意消息获取

详细配置请查看 [部署指南](DEPLOYMENT.md)。

## 管理命令

### 启动和停止

```bash
./start.sh              # 启动机器人
./restart.sh            # 重启机器人
./restart.sh --stop     # 仅停止机器人
./update.sh             # 更新到最新版本
```

### 检查状态

```bash
ps aux | grep "python.*main.py"  # 查看进程
tail -f logs/bot.log             # 查看日志
```

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
| `/search <关键词>` | 搜索帖子 | `/search Python教程` |
| `/hot [数量] [时间]` | 热门排行 | `/hot 20 week` |
| `/tags [数量]` | 标签云 | `/tags 50` |
| `/mystats` | 我的统计 | `/mystats` |
| `/myposts [数量]` | 我的投稿 | `/myposts 20` |

时间参数：`day`（今日）、`week`（本周）、`month`（本月）、`all`（全部，默认）

### 管理员命令

| 命令 | 说明 |
|------|------|
| `/debug` | 系统状态 |
| `/blacklist_add <ID> [原因]` | 添加黑名单 |
| `/blacklist_remove <ID>` | 移除黑名单 |
| `/blacklist_list` | 查看黑名单 |
| `/searchuser <ID>` | 查询用户投稿 |

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
```

高级搜索：
```
/search Python -t week      # 限定时间范围
/search 教程 -n 20          # 限定结果数量
/search #Python -t month -n 15  # 组合使用
```

搜索特性：
- 中文分词优化（jieba）
- 多字段匹配（标题/描述/标签）
- 按相关度和热度排序
- 时间范围筛选

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
├── install.sh           # 一键安装脚本
├── deploy.sh            # Docker 部署脚本
├── update.sh            # 更新脚本
├── start.sh             # 启动脚本
├── restart.sh           # 重启脚本
└── requirements.txt     # Python 依赖
```

## 系统要求

**最低配置：**
- 操作系统：Linux / macOS / Windows (WSL2)
- Python：>= 3.10
- 内存：>= 512 MB
- 磁盘：>= 1 GB
- 网络：可访问 api.telegram.org

**推荐配置：**
- 操作系统：Ubuntu 22.04 LTS / Debian 12
- Python：3.11+
- 内存：>= 1 GB
- 磁盘：>= 5 GB
- CPU：>= 2 核

## 文档

| 文档 | 说明 |
|------|------|
| [README](README.md) | 项目介绍、快速开始 |
| [部署指南](DEPLOYMENT.md) | 详细部署步骤、故障排查 |
| [管理员指南](ADMIN_GUIDE.md) | 管理功能、系统维护 |
| [更新日志](CHANGELOG.md) | 版本历史、功能更新 |

推荐阅读顺序：
1. 首次部署：README → 部署指南
2. 日常使用：README（命令部分）
3. 管理维护：管理员指南
4. 更新系统：运行 `./update.sh`

## 故障排查

**机器人无法启动？**
1. 检查配置文件：`python3 check_config.py`
2. 查看日志：`tail -f logs/bot.log`
3. 检查进程：`ps aux | grep python`

**搜索功能异常？**
1. 重建搜索索引：`python3 migrate_to_search.py`
2. 检查索引目录：`ls -la data/search_index/`

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
