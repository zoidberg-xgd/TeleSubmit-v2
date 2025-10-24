# 🚀 TeleSubmit v2 部署指南

完整的部署指南，涵盖多种部署方式和平台。

## 📋 目录

- [快速开始](#快速开始)
- [部署方式](#部署方式)
  - [方式 1: 一键安装](#方式-1-一键安装推荐)
  - [方式 2: Docker Compose](#方式-2-docker-compose)
  - [方式 3: Systemd 服务](#方式-3-systemd-服务)
  - [方式 4: 直接运行](#方式-4-直接运行)
- [环境要求](#环境要求)
- [配置说明](#配置说明)
- [更新和维护](#更新和维护)
- [故障排查](#故障排查)

---

## 🎯 快速开始

### 最简单的方式（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 2. 运行一键安装脚本
chmod +x install.sh
./install.sh
```

安装脚本会：
- ✅ 自动检测系统环境
- ✅ 检查并安装依赖
- ✅ 引导您完成配置
- ✅ 选择最佳部署方式
- ✅ 自动启动服务

### 或使用快速启动脚本

```bash
chmod +x quickstart.sh
./quickstart.sh
```

---

## 🔧 部署方式

### 方式 1: 一键安装（推荐）

**适用场景**：首次部署、不熟悉 Linux 的用户

**优点**：
- 🎯 自动化程度高
- 🔍 智能检测环境
- 📝 交互式配置向导
- 🛡️ 自动备份数据

**步骤**：

```bash
# 下载并运行安装脚本
chmod +x install.sh
./install.sh
```

脚本会引导您完成：
1. 系统环境检测
2. 依赖检查和安装
3. 部署方式选择
4. 配置文件创建
5. 服务启动

---

### 方式 2: Docker Compose

**适用场景**：生产环境、需要隔离性、多服务部署

**优点**：
- 🐳 容器化部署，环境隔离
- 🔄 易于迁移和备份
- 📦 依赖自动管理
- 🛡️ 资源限制和保护

#### 前置要求

- Docker >= 20.10
- Docker Compose >= 1.29

#### 安装 Docker（如果未安装）

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**CentOS/RHEL:**
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

#### 部署步骤

```bash
# 1. 创建配置文件
cp config.ini.example config.ini
nano config.ini  # 编辑配置

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 或手动部署
docker-compose build
docker-compose up -d
```

#### Docker 管理命令

```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 完全删除
docker-compose down -v

# 进入容器
docker exec -it telesubmit-v2 /bin/bash
```

#### 使用 Makefile

```bash
# 查看所有可用命令
make help

# 部署
make deploy

# 查看日志
make logs

# 重启
make restart

# 备份数据
make backup

# 更新
make update
```

---

### 方式 3: Systemd 服务

**适用场景**：Linux 服务器、需要开机自启、生产环境

**优点**：
- 🔄 开机自动启动
- 📊 系统级服务管理
- 🔍 统一的日志管理
- 🛡️ 自动重启保护

#### 前置要求

- Linux 系统（支持 systemd）
- Python >= 3.10
- sudo 权限

#### 部署步骤

```bash
# 1. 安装 Python 依赖
pip3 install -r requirements.txt

# 2. 创建配置文件
cp config.ini.example config.ini
nano config.ini  # 编辑配置

# 3. 创建 systemd 服务文件
sudo nano /etc/systemd/system/telesubmit.service
```

将以下内容写入服务文件：

```ini
[Unit]
Description=TeleSubmit v2 - Telegram Submission Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/TeleSubmit-v2
ExecStart=/usr/bin/python3 -u /path/to/TeleSubmit-v2/main.py
Restart=always
RestartSec=10
StandardOutput=append:/path/to/TeleSubmit-v2/logs/bot.log
StandardError=append:/path/to/TeleSubmit-v2/logs/error.log

# 环境变量
Environment="PYTHONUNBUFFERED=1"

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**注意**：将 `YOUR_USERNAME` 和 `/path/to/TeleSubmit-v2` 替换为实际值。

```bash
# 4. 重载 systemd 配置
sudo systemctl daemon-reload

# 5. 启用服务（开机自启）
sudo systemctl enable telesubmit

# 6. 启动服务
sudo systemctl start telesubmit

# 7. 检查状态
sudo systemctl status telesubmit
```

#### Systemd 管理命令

```bash
# 查看状态
sudo systemctl status telesubmit

# 启动服务
sudo systemctl start telesubmit

# 停止服务
sudo systemctl stop telesubmit

# 重启服务
sudo systemctl restart telesubmit

# 查看日志
sudo journalctl -u telesubmit -f

# 查看最近 100 行日志
sudo journalctl -u telesubmit -n 100

# 禁用开机自启
sudo systemctl disable telesubmit
```

---

### 方式 4: 直接运行

**适用场景**：开发测试、临时使用、macOS

**优点**：
- 🚀 启动快速
- 🔍 便于调试
- 📝 适合开发

#### 前置要求

- Python >= 3.10

#### 部署步骤

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 创建配置
cp config.ini.example config.ini
nano config.ini  # 编辑配置

# 3. 启动
chmod +x start.sh
./start.sh

# 或直接运行
python3 main.py
```

#### 后台运行

使用 `screen` 或 `tmux`：

```bash
# 使用 screen
screen -S telesubmit
./start.sh
# 按 Ctrl+A+D 分离会话

# 恢复会话
screen -r telesubmit

# 使用 tmux
tmux new -s telesubmit
./start.sh
# 按 Ctrl+B+D 分离会话

# 恢复会话
tmux attach -t telesubmit
```

使用 `nohup`：

```bash
nohup python3 -u main.py > logs/bot.log 2>&1 &
```

---

## 📦 环境要求

### 最低要求

| 组件 | 版本要求 |
|------|---------|
| Python | >= 3.10 |
| 内存 | >= 512MB |
| 磁盘 | >= 1GB |
| 系统 | Linux / macOS |

### 推荐配置

| 组件 | 推荐版本 |
|------|---------|
| Python | 3.11+ |
| 内存 | >= 1GB |
| 磁盘 | >= 5GB |
| CPU | >= 1核 |

### 依赖包

所有 Python 依赖在 `requirements.txt` 中列出：

```txt
python-telegram-bot>=20.0
whoosh>=2.7.4
jieba>=0.42.1
Pillow>=10.0.0
```

---

## ⚙️ 配置说明

### 必要配置

在 `config.ini` 中必须设置：

```ini
[Telegram]
TOKEN = your_bot_token_here        # Bot Token
CHANNEL_ID = @your_channel         # 频道 ID
OWNER_ID = 123456789               # 所有者 ID
```

### 获取配置值

1. **Bot Token**：
   - 联系 [@BotFather](https://t.me/BotFather)
   - 发送 `/newbot` 创建机器人
   - 获取 Token

2. **频道 ID**：
   - 公开频道：直接使用 `@channel_username`
   - 私有频道：转发频道消息给 [@userinfobot](https://t.me/userinfobot) 获取 ID

3. **所有者 ID**：
   - 发送消息给 [@userinfobot](https://t.me/userinfobot)
   - 获取您的用户 ID

### 可选配置

```ini
[Bot]
BOT_MODE = MIXED              # 运行模式：MIXED/SUBMISSION_ONLY/SEARCH_ONLY
ENABLE_NOTIFICATIONS = yes    # 启用通知
MEDIA_VALIDATION = strict     # 媒体验证：strict/basic/none

[Search]
ENABLE_SEARCH = yes          # 启用搜索
MAX_SEARCH_RESULTS = 50      # 最大搜索结果数

[Admin]
ADMIN_IDS = 123,456,789      # 管理员 ID（逗号分隔）
```

### 使用配置向导

```bash
python3 setup_wizard.py
```

配置向导会：
- 📝 交互式输入所有配置
- ✅ 自动验证配置格式
- 💾 生成 `config.ini` 文件
- 🔍 检查 Bot Token 有效性

---

## 🔄 更新和维护

### 更新到最新版本

#### 自动更新（推荐）

```bash
chmod +x update.sh
./update.sh
```

更新脚本会：
- 📦 自动备份当前数据
- ⬇️ 拉取最新代码
- 🔨 重新构建/重启服务
- 📊 显示更新日志

#### 手动更新

**Docker 部署**：
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Systemd 部署**：
```bash
git pull
pip3 install -r requirements.txt --upgrade
sudo systemctl restart telesubmit
```

**直接运行**：
```bash
git pull
pip3 install -r requirements.txt --upgrade
# 重启应用
```

### 数据备份

#### 使用 Makefile

```bash
make backup
```

#### 手动备份

```bash
# 创建备份目录
mkdir -p backups

# 备份数据
tar -czf backups/backup-$(date +%Y%m%d-%H%M%S).tar.gz \
    config.ini \
    data/ \
    logs/
```

#### 恢复备份

```bash
# 解压备份
tar -xzf backups/backup-XXXXXXXX-XXXXXX.tar.gz
```

### 数据迁移

从旧版本迁移数据：

```bash
# 运行迁移脚本
python3 migrate_to_search.py
```

---

## 🔍 故障排查

### 常见问题

#### 1. Bot 无法启动

**检查配置**：
```bash
python3 check_config.py
```

**检查日志**：
```bash
# Docker
docker-compose logs

# Systemd
sudo journalctl -u telesubmit -n 50

# 直接运行
tail -f logs/error.log
```

#### 2. 无法连接到 Telegram

**检查网络**：
```bash
ping api.telegram.org
```

**检查 Token**：
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

#### 3. 搜索功能不工作

**重建搜索索引**：
```bash
python3 migrate_to_search.py
```

**检查索引目录**：
```bash
ls -la data/search_index/
```

#### 4. 数据库错误

**检查数据库文件**：
```bash
ls -la data/*.db
sqlite3 data/submissions.db "PRAGMA integrity_check;"
```

#### 5. 权限错误

**修复文件权限**：
```bash
chmod -R 755 data/ logs/
chown -R $USER:$USER data/ logs/
```

### 日志位置

| 部署方式 | 日志位置 |
|---------|---------|
| Docker | `docker-compose logs` |
| Systemd | `journalctl -u telesubmit` |
| 直接运行 | `logs/bot.log`, `logs/error.log` |

### 性能优化

**增加内存限制（Docker）**：

编辑 `docker-compose.yml`：
```yaml
services:
  bot:
    mem_limit: 1g
    memswap_limit: 1g
```

**调整搜索性能**：

编辑 `config.ini`：
```ini
[Search]
MAX_SEARCH_RESULTS = 20    # 减少结果数
CACHE_SIZE = 100          # 增加缓存
```

---

## 🛡️ 安全建议

1. **保护配置文件**：
   ```bash
   chmod 600 config.ini
   ```

2. **使用环境变量**（可选）：
   ```bash
   export TOKEN="your_bot_token"
   export CHANNEL_ID="@your_channel"
   export OWNER_ID="123456789"
   ```

3. **定期备份**：
   ```bash
   # 添加到 crontab
   0 2 * * * cd /path/to/TeleSubmit-v2 && make backup
   ```

4. **更新依赖**：
   ```bash
   pip3 install -r requirements.txt --upgrade
   ```

5. **防火墙配置**：
   - 仅开放必要端口
   - 使用 HTTPS 代理（如需要）

---

## 📞 获取帮助

- 📖 [项目文档](https://github.com/zoidberg-xgd/TeleSubmit-v2)
- 🐛 [问题反馈](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues)
- 💬 Telegram 群组：查看 README

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

