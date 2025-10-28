# TeleSubmit v2 部署指南

本文档详细介绍 TeleSubmit v2 的部署步骤和配置说明。

## 前置准备

### 系统要求

- **操作系统**: Linux / macOS / Windows (WSL)
- **Python**: 3.9+ (推荐 3.11)
- **内存**: 256 MB - 1 GB
- **磁盘空间**: 100 MB 以上
- **网络**: 能够访问 Telegram API

### 获取必要信息

部署前请准备以下信息：

1. **Bot Token**
   - 向 [@BotFather](https://t.me/BotFather) 发送 `/newbot` 创建机器人
   - 格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **频道 ID**
   - 频道用户名：`@your_channel`（必须是公开频道）
   - 或数字 ID：`-1001234567890`（私有频道）
   - 获取数字 ID：将 Bot 添加为频道管理员后，转发频道消息给 [@userinfobot](https://t.me/userinfobot)

3. **管理员 ID**
   - 向 [@userinfobot](https://t.me/userinfobot) 发送任意消息获取您的 User ID
   - 格式：`123456789`

4. **频道设置**
   - 将 Bot 添加为频道管理员
   - 授予以下权限：
     - ✓ 发送消息
     - ✓ 编辑消息
     - ✓ 删除消息
     - ✓ 管理消息

## 部署方式

### 方式一：快速启动（推荐新手）

最简单的部署方式，适合初次使用：

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
./quickstart.sh
```

快速启动脚本会：
1. 检测系统环境
2. 推荐适合的部署方式
3. 引导完成配置
4. 自动启动服务

### 方式二：一键安装（完整向导）

包含交互式配置向导：

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
./install.sh
```

安装流程：
1. 检查 Python 和依赖
2. 创建必要目录
3. 安装 Python 包
4. 交互式配置（Bot Token、频道 ID、管理员 ID）
5. 初始化数据库
6. 询问是否启动

### 方式三：Docker 部署（生产环境推荐）

适合生产环境和需要容器隔离的场景：

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
cp config.ini.example config.ini
nano config.ini  # 编辑配置文件
./deploy.sh
```

**⚡️ 快速启动选项**：

如果您已经有构建好的镜像，想要快速重启服务（跳过漫长的构建过程）：

```bash
# ⚡️ 快速启动模式（推荐日常使用）
./deploy.sh --fast
```

这个选项会：
- ✅ 跳过 Docker 镜像构建
- ✅ 直接使用现有镜像启动
- ✅ 几秒钟内完成部署
- ⚠️ 需要先有已构建的镜像

**在网络受限环境中使用代理**：

如果您在中国大陆或其他网络受限地区，Docker 构建可能会卡住（拉取镜像、安装依赖等）。您可以使用代理服务器：

```bash
# 使用本地代理部署（推荐）
./deploy.sh --proxy http://127.0.0.1:7890

# 使用网络代理
./deploy.sh --proxy http://192.168.1.100:7890

# 使用代理并重新构建镜像
./deploy.sh --rebuild --proxy http://127.0.0.1:7890

# 查看所有选项
./deploy.sh --help
```

**重要说明**：
- 脚本会自动将 `localhost`/`127.0.0.1` 转换为 `host.docker.internal`，使容器能访问宿主机代理
- 确保代理软件允许来自局域网的连接（不只是 localhost）
- 如遇连接问题，请查看 [故障排查指南](DEPLOY_TROUBLESHOOTING.md#网络问题)

**常见代理软件端口**：
- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809`
- Shadowsocks: `socks5://127.0.0.1:1080` (需转换为 http)

> 💡 **提示**：确保代理软件已启动并开启"允许局域网连接"选项

**Docker 优势**：
- 环境隔离，不影响主机
- 自动重启，服务更稳定
- 易于迁移和扩展

**Docker 管理**：
```bash
docker-compose ps              # 查看状态
docker-compose logs -f         # 查看日志
docker-compose restart         # 重启容器
docker-compose down            # 停止并删除容器
./deploy.sh --rebuild          # 重新构建镜像
```

### 方式四：手动部署（高级用户）

完全手动控制部署过程：

```bash
# 1. 克隆仓库
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 配置
cp config.ini.example config.ini
nano config.ini

# 5. 初始化数据库
python3 -c "from utils.database import init_db; init_db()"

# 6. 启动
./start.sh
```

## 配置说明

### 必填配置

编辑 `config.ini` 文件，配置以下必填项：

```ini
[BOT]
TOKEN = your_bot_token_here        # Bot Token
CHANNEL_ID = @your_channel         # 频道 ID
OWNER_ID = 123456789               # 管理员 User ID
```

### 可选配置

```ini
[BOT]
# 数据库文件路径（投稿与索引所用的 SQLite 数据库）
DB_PATH = data/submissions.db

# 会话超时时间（秒）
TIMEOUT = 300

# 单次投稿允许的最大标签数量
ALLOWED_TAGS = 30

# 额外管理员（逗号分隔，整数 ID）。OWNER_ID 会自动加入
# ADMIN_IDS = 123456789,987654321

# 在频道帖中是否显示投稿人（true/false）
SHOW_SUBMITTER = true

# 是否向所有者发送新投稿通知（true/false）
NOTIFY_OWNER = true

# 机器人工作模式：MEDIA（仅媒体）、DOCUMENT（仅文档）、MIXED（混合）
BOT_MODE = MIXED

# 运行模式：POLLING（轮询）| WEBHOOK（Webhook）
# - POLLING: 默认模式，机器人主动拉取消息，适合开发和小型部署
# - WEBHOOK: Telegram 推送消息到服务器，适合生产环境，更高效
RUN_MODE = POLLING

# 允许上传的文档类型（后缀或 MIME，逗号分隔；* 表示全部）
ALLOWED_FILE_TYPES = *

[WEBHOOK]
# Webhook 模式配置（仅当 BOT.RUN_MODE = WEBHOOK 时生效）

# 外部访问地址（必填，例如: https://your-domain.com）
# 注意：必须是 HTTPS 且有效的域名
URL = 

# Webhook 监听端口（默认 8080）
PORT = 8080

# Webhook 路径（默认 /webhook）
PATH = /webhook

# Webhook Secret Token（可选，用于验证请求来源）
# 留空则自动生成随机 token
SECRET_TOKEN = 

[SEARCH]
# 搜索引擎配置
INDEX_DIR = data/search_index      # 索引目录
ENABLED = true                     # 是否启用搜索
```

#### 环境变量覆盖

支持用环境变量覆盖同名配置（环境变量优先）。常用示例：

```bash
export TOKEN="123456:ABC..."             # 等价于 [BOT].TOKEN
export CHANNEL_ID="@your_channel"        # 等价于 [BOT].CHANNEL_ID
export OWNER_ID="123456789"              # 等价于 [BOT].OWNER_ID
export ADMIN_IDS="123,456"               # 等价于 [BOT].ADMIN_IDS
export SHOW_SUBMITTER="true"             # 等价于 [BOT].SHOW_SUBMITTER
export NOTIFY_OWNER="true"               # 等价于 [BOT].NOTIFY_OWNER
export BOT_MODE="MIXED"                  # 等价于 [BOT].BOT_MODE
export RUN_MODE="WEBHOOK"                # 等价于 [BOT].RUN_MODE
export ALLOWED_FILE_TYPES=".pdf,.zip"    # 等价于 [BOT].ALLOWED_FILE_TYPES

export WEBHOOK_URL="https://your-domain.com"  # 等价于 [WEBHOOK].URL
export WEBHOOK_PORT="8080"                    # 等价于 [WEBHOOK].PORT
export WEBHOOK_PATH="/webhook"                # 等价于 [WEBHOOK].PATH
export WEBHOOK_SECRET_TOKEN="your_token"      # 等价于 [WEBHOOK].SECRET_TOKEN

export SEARCH_INDEX_DIR="data/search_index"  # 覆盖 [SEARCH].INDEX_DIR
export SEARCH_ENABLED="true"                 # 覆盖 [SEARCH].ENABLED
```

### 验证配置

使用配置检查工具验证：

```bash
python3 check_config.py
```

## 运行模式配置

TeleSubmit v2 支持两种运行模式，可根据部署环境选择：

### Polling 模式（默认）

**适用场景**：本地开发、测试环境、无公网域名

**特点**：
- 机器人主动拉取消息
- 配置简单，无需额外设置
- 网络消耗较高，响应延迟 1-3 秒

**配置**：
```ini
[BOT]
RUN_MODE = POLLING
```

### Webhook 模式

**适用场景**：生产环境、云服务器、有 HTTPS 域名

**特点**：
- Telegram 推送消息到服务器
- 响应快（<1秒）、资源消耗低
- 需要 HTTPS 公网域名

**配置**：
```ini
[BOT]
RUN_MODE = WEBHOOK

[WEBHOOK]
URL = https://your-domain.com
PORT = 8080
PATH = /webhook
SECRET_TOKEN = your_random_token  # 可选
```

**环境变量方式**：
```bash
export RUN_MODE=WEBHOOK
export WEBHOOK_URL=https://your-domain.com
export WEBHOOK_PORT=8080
export WEBHOOK_PATH=/webhook
export WEBHOOK_SECRET_TOKEN=your_random_token
```

**模式切换**：
- 修改配置后使用 `./restart.sh` 重启即可
- 系统会自动处理模式切换和清理

详细说明请查看 [Webhook 模式完整指南](docs/WEBHOOK_MODE.md)。

## 启动和管理

### 启动服务

```bash
./start.sh                    # 后台启动
python3 main.py               # 前台启动（调试用）
```

### 查看状态

```bash
# 查看进程
ps aux | grep "python.*main.py"

# 查看日志
tail -f logs/bot.log          # 标准日志
tail -f logs/error.log        # 错误日志
```

### 停止服务

```bash
./restart.sh --stop           # 使用脚本停止
pkill -f "python.*main.py"    # 手动停止
```

### 重启服务

```bash
./restart.sh                  # 正常重启
./restart.sh --force          # 强制重启
```

## 数据库管理

### 初始化数据库

首次部署时会自动创建数据库，手动初始化：

```bash
python3 -c "from utils.database import init_db; init_db()"
```

### 数据库备份

```bash
# 自动备份（每次重启时）
./restart.sh

# 手动备份
cp data/posts.db backups/posts_$(date +%Y%m%d_%H%M%S).db
cp data/submissions.db backups/submissions_$(date +%Y%m%d_%H%M%S).db
```

### 数据库恢复

```bash
# 恢复备份
cp backups/posts_YYYYMMDD_HHMMSS.db data/posts.db
cp backups/submissions_YYYYMMDD_HHMMSS.db data/submissions.db
./restart.sh
```

### 数据库优化

```bash
python3 optimize_database.py
```

## 搜索索引管理

### 初始化索引

```bash
<<<<<<< HEAD
# 初次建立索引（自动进行）
python3 -c "from utils.search_engine import PostSearchEngine; PostSearchEngine().initialize()"
=======
# 初次建立索引（系统运行时也会自动创建）
python3 -c "from utils.search_engine import init_search_engine; init_search_engine('data/search_index', from_scratch=True)"
>>>>>>> 12388294350dae5817f4c4b569651c95b018524a
```

### 重建索引

当搜索出现问题时：

```bash
python3 utils/index_manager.py rebuild
```

### 查看索引状态

```bash
python3 utils/index_manager.py status
```

更多索引管理信息请查看 [索引管理器文档](INDEX_MANAGER_README.md)。

## 更新和升级

### 常规更新

拉取最新代码并重启：

```bash
./update.sh
```

### 功能升级

包含数据库迁移的大版本升级：

```bash
./upgrade.sh
```

升级前会自动备份数据库。

### 手动更新

```bash
git pull
pip3 install -r requirements.txt --upgrade
./restart.sh
```

## 故障排查

### 机器人无法启动

**症状**：运行 `./start.sh` 后进程立即退出

**排查步骤**：
1. 查看错误日志：`tail -f logs/error.log`
2. 检查配置文件：`python3 check_config.py`
3. 验证 Bot Token：确认 Token 正确且未过期
4. 检查网络连接：`curl -I https://api.telegram.org`

**常见原因**：
- Token 配置错误
- 网络无法访问 Telegram API
- Python 版本不兼容
- 缺少依赖包

### 无法连接数据库

**症状**：日志显示 `database is locked` 或连接错误

**解决方法**：
```bash
# 检查数据库文件权限
ls -la data/*.db

# 修复权限
chmod 664 data/*.db

# 检查是否有多个实例运行
ps aux | grep main.py
pkill -f "python.*main.py"

# 重启服务
./restart.sh
```

### 搜索功能异常

**症状**：搜索无结果或报错

**解决方法**：
```bash
# 重建搜索索引
python3 utils/index_manager.py rebuild

# 检查索引状态
python3 utils/index_manager.py status

# 如果仍有问题，删除并重建
rm -rf data/search_index
python3 utils/index_manager.py rebuild
```

### 内存占用过高

**症状**：系统内存不足或 OOM

**解决方法**：
1. 检查内存使用：
   - 机器人内置命令：在私聊中发送 `/debug` 查看实时内存
   - Docker 环境：
     ```bash
     docker stats telesubmit-v2
     ```
   - 系统工具：
     ```bash
     top -o mem   # 或 htop
     ```

2. 优化数据库：
   ```bash
   python3 optimize_database.py
   ```

3. 调整配置（`config.ini`）：
```ini
   [SEARCH]
   ENABLED = true
   ```

详细内存分析请查看 [内存占用说明](MEMORY_USAGE.md)。

### 频道消息发送失败

**症状**：投稿无法发布到频道

**排查步骤**：
1. 确认 Bot 是频道管理员
2. 检查频道 ID 配置是否正确
3. 验证 Bot 权限：
   - 发送消息
   - 编辑消息
   - 删除消息

**测试方法**：
```bash
# 在 Bot 私聊中发送测试消息
# 观察 logs/bot.log 中的错误信息
```

### Docker 容器无法启动

**症状**：`docker-compose up` 报错

**解决方法**：
```bash
# 查看详细日志
docker-compose logs

# 重新构建镜像
./deploy.sh --rebuild

# 检查 Docker 服务
sudo systemctl status docker

# 清理旧容器和镜像
docker-compose down
docker system prune -a
./deploy.sh
```

## 性能优化

### 数据库优化

```bash
# 定期运行数据库优化
python3 optimize_database.py

# 设置定时任务（每周一次）
crontab -e
# 添加：0 3 * * 0 cd /path/to/TeleSubmit-v2 && python3 optimize_database.py
```

### 搜索性能优化

如果不需要搜索功能，可以关闭以降低内存占用：

```ini
# config.ini
[SEARCH]
ENABLED = false
```

### 内存优化

对于内存受限的环境（如 256MB 服务器）：

```ini
# config.ini
[SEARCH]
# 禁用搜索以节省内存
ENABLED = false
```

定期清理旧日志：
```bash
# 只保留最近 7 天的日志
find logs/ -name "*.log" -mtime +7 -delete
```

## 安全建议

### 配置文件安全

```bash
# 限制配置文件权限
chmod 600 config.ini

# 不要将 config.ini 提交到 Git
# 已在 .gitignore 中配置
```

### 定期备份

```bash
# 创建定时备份任务
crontab -e

# 每天凌晨 2 点备份
0 2 * * * cd /path/to/TeleSubmit-v2 && tar -czf backups/backup_$(date +\%Y\%m\%d).tar.gz data/ config.ini
```

### 更新维护

```bash
# 定期更新代码
git pull

# 更新依赖包
pip3 install -r requirements.txt --upgrade

# 重启服务
./restart.sh
```

## 监控和日志

### 日志级别

编辑 `utils/logging_config.py` 调整日志级别：

```python
# DEBUG: 详细调试信息
# INFO: 常规信息
# WARNING: 警告信息
# ERROR: 错误信息
```

### 日志轮转

防止日志文件过大：

```bash
# 安装 logrotate（Linux）
sudo apt install logrotate

# 配置 /etc/logrotate.d/telesubmit
/path/to/TeleSubmit-v2/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 监控脚本

创建简单的监控脚本：

```bash
#!/bin/bash
# monitor.sh
if ! pgrep -f "python.*main.py" > /dev/null; then
    echo "Bot 已停止，正在重启..."
    cd /path/to/TeleSubmit-v2
    ./start.sh
fi
```

定时检查：
```bash
crontab -e
# 每 5 分钟检查一次
*/5 * * * * /path/to/monitor.sh
```

## 相关文档

- [部署故障排查](DEPLOY_TROUBLESHOOTING.md) - 解决部署过程中的常见问题
- [脚本使用指南](SCRIPTS_GUIDE.md) - 所有管理脚本详细说明
- [管理员指南](ADMIN_GUIDE.md) - 管理功能和系统维护
- [索引管理器](INDEX_MANAGER_README.md) - 搜索索引管理
- [内存占用说明](MEMORY_USAGE.md) - 内存使用分析
- [更新日志](CHANGELOG.md) - 版本历史

## 获取帮助

如果遇到问题：
1. **部署阶段问题**：查看 [部署故障排查指南](DEPLOY_TROUBLESHOOTING.md)
2. 查看日志文件：`logs/bot.log` 和 `logs/error.log`
3. 检查配置：`python3 check_config.py`
4. 提交 Issue 到 GitHub 仓库

