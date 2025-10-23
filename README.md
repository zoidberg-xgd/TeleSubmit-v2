# TeleSubmit v2 - 电报频道投稿助手

一个帮助用户向 Telegram 频道提交内容的机器人。支持媒体和文档的灵活投稿，提供流畅的用户体验。

## ✨ 功能特点

### 基础功能
- **多种提交模式**: 媒体模式、文档模式、混合模式
- **批量上传**: 媒体最多50个，文档最多10个
- **标签系统**: 可搜索的内容分类标签（必填，最多30个）
- **丰富元数据**: 链接、标题、说明（可选）
- **剧透标记**: 敏感内容需点击查看
- **权限控制**: 所有者管理权限、黑名单功能
- **会话管理**: 自动清理过期会话，防止资源浪费

### 🆕 v2 新增功能
- **📊 热度统计系统**: 基于浏览量、转发数、反应数的智能热度算法
- **🔥 热门帖子排行**: 支持按时间范围（今日/本周/本月）查看热门内容
- **🔍 全文搜索**: 在标题、描述、标签中搜索已发布的帖子
- **🏷️ 标签云**: 查看所有标签及其使用频率
- **📝 我的投稿**: 查看个人投稿历史和统计数据
- **⏰ 自动更新**: 每小时自动更新帖子统计数据
- **👤 用户管理**: 管理员可按用户查询投稿记录

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit.git
cd TeleSubmit

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

首次运行会自动创建配置文件 `config.ini`，按提示编辑后再次运行即可启动。

## 📦 安装方式

### 方式一：Docker 部署（推荐）

**优势**: 环境隔离、一键启动、自动重启、资源管理、数据持久化

**系统要求**: Docker >= 20.10, Docker Compose >= 1.29

```bash
# 使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

### 方式二：传统部署

**系统要求**: Python 3.7+

```bash
# 安装依赖
pip install -r requirements.txt

# 创建配置
cp config.ini.example config.ini
nano config.ini

# 启动机器人
python main.py

# 后台运行
nohup python main.py > output.log 2>&1 &
```

## ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[BOT]
# 必填项
TOKEN = your_bot_token_here          # 从 @BotFather 获取
CHANNEL_ID = @your_channel_name      # 目标频道
OWNER_ID = your_user_id_here         # 从 @userinfobot 获取

# 可选项
DB_PATH = submissions.db             # 数据库路径
TIMEOUT = 300                        # 会话超时（秒）
ALLOWED_TAGS = 30                    # 最多标签数
BOT_MODE = MIXED                     # MEDIA/DOCUMENT/MIXED
SHOW_SUBMITTER = True                # 显示投稿人信息
NOTIFY_OWNER = True                  # 通知所有者
```

## 📖 使用方法

1. 发送 `/start` 开始新的提交
2. 选择提交类型（媒体/文档）
3. 按提示完成投稿流程：
   - 上传文件
   - 添加标签（必填）
   - 添加链接、标题、说明（可选，使用 `/skip_optional` 跳过）
   - 设置剧透
   - 确认提交
4. 使用 `/cancel` 随时取消

### 常用命令

**基础投稿**:
- `/start` - 开始新投稿
- `/done_media` - 完成媒体上传
- `/done_doc` - 完成文档上传
- `/skip_media` - 跳过媒体上传
- `/skip_optional` - 跳过可选字段
- `/cancel` - 取消当前投稿
- `/help` - 查看帮助信息
- `/settings` - 设置偏好

**🆕 统计与搜索**:
- `/hot [数量] [时间]` - 查看热门帖子
  - 例: `/hot` - 查看前10个热门帖子
  - 例: `/hot 20` - 查看前20个热门帖子
  - 例: `/hot 10 week` - 查看本周前10个热门帖子
  - 时间选项: `day`(今日)、`week`(本周)、`month`(本月)
- `/search <关键词> [选项]` - 搜索帖子
  - 例: `/search Python` - 搜索包含Python的帖子
  - 例: `/search #编程` - 搜索带有"编程"标签的帖子
  - 例: `/search 教程 -t week` - 搜索本周的教程
  - 选项: `-t day/week/month` (时间范围), `-n <数量>` (结果数量)
- `/tags [数量]` - 查看标签云
  - 例: `/tags` - 查看前20个热门标签
  - 例: `/tags 50` - 查看前50个热门标签
- `/myposts [数量]` - 查看我的投稿
  - 例: `/myposts` - 查看最近10篇投稿
  - 例: `/myposts 20` - 查看最近20篇投稿
- `/mystats` - 查看我的投稿统计

**管理员**（仅所有者）:
- `/blacklist_add <用户ID> [原因]` - 添加黑名单
- `/blacklist_remove <用户ID>` - 移除黑名单
- `/blacklist_list` - 查看黑名单
- `/searchuser <用户ID>` - 查询指定用户的投稿
- `/debug` - 系统调试信息


## 🎯 使用场景示例

### 1. 查看热门内容
```
/hot 20 week
```
查看本周最热门的20个帖子，快速了解频道热点内容。

### 2. 搜索特定主题
```
/search Python -t month -n 15
```
搜索本月所有关于 Python 的帖子，最多显示15个结果。

### 3. 查看标签趋势
```
/tags 30
```
查看前30个最热门的标签，了解频道内容分布。

### 4. 管理个人投稿
```
/myposts 20
/mystats
```
查看自己的投稿历史和详细统计数据。

## 📁 项目结构

```
TeleSubmit-v2/
├── config/                  # 配置管理
├── database/                # 数据库操作
│   ├── db_manager.py       # 数据库管理（包含统计表）
│   └── __init__.py
├── handlers/                # 消息处理器
│   ├── command_handlers.py # 基础命令处理
│   ├── publish.py          # 发布处理（含保存统计）
│   ├── stats_handlers.py   # 🆕 统计功能处理
│   ├── search_handlers.py  # 🆕 搜索功能处理
│   └── ...                 # 其他处理器
├── models/                  # 数据模型
├── utils/                   # 工具函数
├── data/                    # 数据目录
├── logs/                    # 日志目录
├── main.py                  # 主程序入口
├── config.ini.example       # 配置示例
├── deploy.sh                # 部署脚本
├── docker-compose.yml       # Docker配置
├── Dockerfile               # 镜像构建
└── requirements.txt         # 依赖清单
```

## 🔧 热度算法说明

v2 版本引入了智能热度评分系统：

**热度分数计算公式**:
```
热度分数 = (浏览数 × 0.3 + 转发数 × 10 × 0.4 + 反应数 × 5 × 0.3) × 时间衰减因子
```

**时间衰减**:
- 使用半衰期算法，7天半衰期
- 越新的帖子权重越高
- 保证排行榜既反映热度又兼顾新鲜度

**更新机制**:
- 自动每小时更新一次所有活跃帖子（最近30天）的统计数据
- 避免过度请求 Telegram API

## 📝 依赖项

- python-telegram-bot >= 21.0
- aiosqlite >= 0.17.0
- configparser >= 6.0.0
- python-dotenv >= 1.0.0
- psutil >= 5.9.0

## 📄 许可证

MIT 许可证 - 详见 LICENSE 文件

## 💬 支持

- [GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit/issues)
- 开发者: [@zoidberg-xgd](https://github.com/zoidberg-xgd)
- 项目地址: https://github.com/zoidberg-xgd/TeleSubmit
