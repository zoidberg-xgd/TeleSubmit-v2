# 🚀 TeleSubmit v2 部署指南

## 📋 前置准备

### 1. 获取 Telegram Bot Token

1. 在 Telegram 中找 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 复制获得的 Token（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 创建或准备频道

1. 在 Telegram 中创建一个频道（公开或私有均可）
2. 获取频道 ID：
   - **公开频道**：使用 `@频道用户名`（如 `@mychannel`）
   - **私有频道**：将 [@userinfobot](https://t.me/userinfobot) 添加到频道，它会告诉你频道 ID（如 `-1001234567890`）
3. **重要**：将机器人添加为频道管理员，至少给予「发布消息」权限

### 3. 获取您的 User ID

1. 在 Telegram 中找 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 复制返回的您的 ID（纯数字）

---

## 🐳 Docker 部署（推荐）

### 快速部署

```bash
# 1. 进入项目目录
cd /Users/yaoxiaohang/Documents/xgdbot/TeleSubmit-v2

# 2. 配置机器人（三选一）

## 方式 A：使用配置向导（最简单）
python3 setup_wizard.py

## 方式 B：手动编辑配置文件
cp config.ini.example config.ini
nano config.ini  # 编辑并填入真实配置

## 方式 C：使用环境变量
nano docker-compose.yml  # 取消注释并填入环境变量

# 3. 构建并启动容器
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 检查状态
docker-compose ps
```

### 管理命令

```bash
# 停止容器
docker-compose stop

# 重启容器
docker-compose restart

# 查看实时日志
docker-compose logs -f --tail=100

# 进入容器 shell
docker-compose exec telesubmit bash

# 重新构建（代码更新后）
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 💻 直接运行（开发环境）

### 安装依赖

```bash
# 1. 确保 Python 3.8+ 已安装
python3 --version

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 配置并运行

```bash
# 1. 配置机器人
python3 setup_wizard.py

# 2. 检查配置
python3 check_config.py

# 3. 启动机器人
python3 main.py

# 或使用启动脚本
./start.sh
```

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
docker-compose ps
```

应该看到：
```
NAME              STATUS          PORTS
telesubmit-v2     Up X seconds    
```

### 2. 查看日志

```bash
docker-compose logs -f
```

成功启动应该看到：
```
✅ 数据库初始化完成
✅ 搜索引擎初始化完成
🤖 机器人启动成功！开始监听消息...
```

### 3. 测试机器人

在 Telegram 中：

1. 找到您的机器人（搜索创建时的用户名）
2. 发送 `/start` - 应该收到欢迎消息
3. 发送 `/help` - 查看所有命令
4. 发送 `/submit` - 测试投稿功能

---

## 🔧 故障排查

### 问题 1：容器无法启动

```bash
# 查看详细日志
docker-compose logs

# 检查配置
python3 check_config.py

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 问题 2：机器人无响应

**检查清单：**
- ✅ Token 是否正确？
- ✅ 网络连接是否正常？
- ✅ 容器是否正在运行？（`docker-compose ps`）
- ✅ 日志中是否有错误？（`docker-compose logs`）

### 问题 3：无法发送到频道

**检查清单：**
- ✅ 机器人是否已添加为频道管理员？
- ✅ 频道 ID 是否正确？
- ✅ 机器人是否有「发布消息」权限？

### 问题 4：搜索功能不工作

```bash
# 检查搜索索引
docker-compose exec telesubmit ls -la data/search_index

# 重新构建索引
docker-compose exec telesubmit python3 migrate_to_search.py

# 查看搜索日志
docker-compose logs | grep -i search
```

---

## 📊 数据迁移

如果您从 v1 升级或需要导入旧数据：

```bash
# 确保旧数据库文件在正确位置
# 默认位置：data/submissions.db

# 运行迁移脚本
docker-compose exec telesubmit python3 migrate_to_search.py

# 或在本地运行
python3 migrate_to_search.py
```

---

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 停止容器
docker-compose down

# 3. 重新构建
docker-compose build --no-cache

# 4. 启动
docker-compose up -d

# 5. 验证
docker-compose logs -f
```

---

## 📁 目录结构

```
TeleSubmit-v2/
├── config.ini          # 配置文件（需要手动创建）
├── data/               # 持久化数据（自动创建）
│   ├── submissions.db  # SQLite 数据库
│   └── search_index/   # Whoosh 搜索索引
├── logs/               # 日志文件（自动创建）
│   └── bot.log
└── docker-compose.yml  # Docker 配置
```

---

## 🎯 测试清单

部署完成后，按顺序测试以下功能：

- [ ] 基础命令
  - [ ] `/start` - 欢迎消息
  - [ ] `/help` - 帮助信息
  - [ ] `/cancel` - 取消操作

- [ ] 投稿功能
  - [ ] `/submit` - 开始投稿
  - [ ] 上传媒体/文档
  - [ ] 添加标签
  - [ ] 预览和发布

- [ ] 搜索功能
  - [ ] `/search 关键词` - 关键词搜索
  - [ ] `/search #标签` - 标签搜索
  - [ ] `/tags` - 查看标签云

- [ ] 统计功能
  - [ ] `/hot` - 热门排行
  - [ ] `/myposts` - 我的投稿
  - [ ] `/mystats` - 个人统计

- [ ] 管理功能（需要 OWNER_ID）
  - [ ] `/blacklist` - 黑名单管理
  - [ ] `/stats` - 全站统计

---

## 💡 最佳实践

1. **安全性**
   - 不要将 `config.ini` 提交到 Git
   - 定期备份 `data/` 目录
   - 使用环境变量存储敏感信息

2. **性能优化**
   - 定期清理旧日志：`find logs/ -name "*.log" -mtime +30 -delete`
   - 监控容器资源使用：`docker stats telesubmit-v2`

3. **运维建议**
   - 使用 `docker-compose` 管理容器
   - 配置日志轮转（已在 docker-compose.yml 中配置）
   - 定期更新依赖包

---

## 📞 获取帮助

遇到问题？

1. 查看 [README.md](README.md) - 完整文档
2. 查看 [QUICKSTART.md](QUICKSTART.md) - 快速开始
3. 查看 [SEARCH_QUICKSTART.md](SEARCH_QUICKSTART.md) - 搜索功能
4. 运行 `python3 check_config.py` - 配置诊断

---

**祝您使用愉快！🎉**

