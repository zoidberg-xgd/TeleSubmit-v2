# Fly.io Webhook 模式部署指南

本指南详细说明如何在 Fly.io 上以 Webhook 模式部署 TeleSubmit v2 项目。

---

## 📋 前提条件

### 必需信息

- Telegram Bot Token（从 [@BotFather](https://t.me/BotFather) 获取）
- 频道 ID 或用户名
- 管理员 User ID（从 [@userinfobot](https://t.me/userinfobot) 获取）
- Fly.io 账号（访问 [fly.io](https://fly.io) 注册，需要信用卡验证但免费额度内不收费）

### 安装工具

安装 Fly.io CLI 工具：

**macOS/Linux**:
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

验证安装：
```bash
flyctl version
```

---

## 🚀 部署步骤

### 第一步：登录 Fly.io

```bash
flyctl auth login
```

这会打开浏览器进行登录验证。

---

### 第二步：准备项目

克隆或进入项目目录：

```bash
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
```

---

### 第三步：配置 fly.toml

项目已包含 `fly.toml` 配置文件，如果没有，创建它：

```bash
cat > fly.toml << 'EOF'
# Fly.io 应用配置文件
app = ""  # 应用名称，留空由 fly launch 自动生成

[build]
  dockerfile = "Dockerfile"

[env]
  # 运行模式：必须设置为 WEBHOOK
  RUN_MODE = "WEBHOOK"
  
  # Webhook 端口（Fly.io 内部端口）
  WEBHOOK_PORT = "8080"
  
  # Webhook 路径
  WEBHOOK_PATH = "/webhook"
  
  # 搜索引擎优化（使用轻量级分词器节省内存）
  SEARCH_ANALYZER = "simple"
  
  # 数据库缓存优化
  DB_CACHE_KB = "1024"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
EOF
```

---

### 第四步：创建配置文件

创建 `config.ini`（如果还没有）：

```bash
cp config.ini.example config.ini
nano config.ini
```

编辑关键配置：

```ini
[BOT]
# 从 @BotFather 获取
TOKEN = your_bot_token_here

# 频道 ID 或用户名
CHANNEL_ID = @your_channel

# 管理员 User ID
OWNER_ID = 123456789

# ⭐ 重要：设置为 WEBHOOK 模式
RUN_MODE = WEBHOOK

[WEBHOOK]
# ⚠️ 注意：URL 会在部署后自动设置，这里先留空或填占位符
# 格式: https://your-app-name.fly.dev
URL = 

# 端口和路径（与 fly.toml 保持一致）
PORT = 8080
PATH = /webhook

[SEARCH]
# 使用轻量级分词器节省内存
ANALYZER = simple

[DB]
# 内存优化配置
CACHE_SIZE_KB = 1024
```

---

### 第五步：创建应用并部署

#### 1. 初始化应用

```bash
flyctl launch
```

这个命令会：
- 检测到 Dockerfile
- 询问应用名称（可以接受默认名称或自定义）
- 询问部署区域（选择离您最近的，如 `hkg` 香港、`nrt` 东京、`sjc` 美国）
- 询问是否立即部署（选择 No，我们先设置密钥）

**示例输出**：
```
? Choose an app name (leave blank to generate one): my-telegram-bot
? Choose a region for deployment: Hong Kong, Hong Kong (hkg)
? Would you like to deploy now? No
```

记下您的应用名称，例如 `my-telegram-bot`，您的应用 URL 将是：
```
https://my-telegram-bot.fly.dev
```

#### 2. 设置密钥（Secrets）

使用 Fly.io 的 Secrets 功能安全地存储敏感信息：

```bash
# 设置 Bot Token（⭐ 替换为实际 Token）
flyctl secrets set BOT_TOKEN=your_bot_token_here

# 设置频道 ID
flyctl secrets set CHANNEL_ID=@your_channel

# 设置管理员 ID
flyctl secrets set OWNER_ID=123456789

# 设置 Webhook URL（⭐ 替换为您的应用名称）
flyctl secrets set WEBHOOK_URL=https://your-app-name.fly.dev
```

**完整示例**：
```bash
flyctl secrets set BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
flyctl secrets set CHANNEL_ID=@mychannel
flyctl secrets set OWNER_ID=987654321
flyctl secrets set WEBHOOK_URL=https://my-telegram-bot.fly.dev
```

#### 3. 部署应用

```bash
flyctl deploy
```

部署过程：
1. 构建 Docker 镜像
2. 推送到 Fly.io 注册表
3. 启动应用实例
4. 自动配置 HTTPS

**等待部署完成**，通常需要 2-5 分钟。

---

### 第六步：设置 Webhook

部署完成后，设置 Telegram Webhook：

```bash
# ⭐ 替换为您的实际信息
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -d "url=https://your-app-name.fly.dev/webhook" \
  -d "max_connections=40"
```

**示例**：
```bash
curl -X POST "https://api.telegram.org/bot123456:ABC-DEF/setWebhook" \
  -d "url=https://my-telegram-bot.fly.dev/webhook" \
  -d "max_connections=40"
```

**验证 Webhook**：

```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

应该看到：
```json
{
  "ok": true,
  "result": {
    "url": "https://your-app-name.fly.dev/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

---

## ✅ 验证部署

### 1. 检查应用状态

```bash
flyctl status
```

应该显示：
```
ID              = my-telegram-bot
Status          = running
...
```

### 2. 查看日志

```bash
flyctl logs
```

应该看到：
```
✅ Webhook 模式已启动
   监听地址: 0.0.0.0:8080/webhook
   外部地址: https://my-telegram-bot.fly.dev/webhook
```

### 3. 测试健康检查

```bash
curl https://your-app-name.fly.dev/health
```

应该返回：`OK`

### 4. 测试机器人

向您的 Telegram 机器人发送消息：
- 发送 `/start` 命令
- 应该立即收到回复（< 1 秒）

---

## 🔧 常见问题解决

### 问题 1：部署失败

**症状**：`flyctl deploy` 报错

**解决方法**：

```bash
# 查看详细错误
flyctl logs

# 常见原因：
# 1. Dockerfile 路径错误
ls -la Dockerfile

# 2. 依赖安装失败
# 检查 requirements.txt 是否存在

# 3. 重新部署
flyctl deploy --force
```

### 问题 2：机器人无响应

**可能原因**：
1. Webhook 未正确设置
2. 环境变量配置错误
3. 应用未运行

**解决方法**：

```bash
# 1. 检查应用状态
flyctl status

# 2. 查看日志
flyctl logs

# 3. 检查 Secrets
flyctl secrets list

# 4. 验证 Webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"

# 5. 重启应用
flyctl apps restart your-app-name
```

### 问题 3：内存不足

**症状**：应用频繁重启，日志显示 OOM (Out of Memory)

**解决方法**：

升级内存配额（编辑 `fly.toml`）：

```toml
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512  # 从 256MB 升级到 512MB
```

然后重新部署：
```bash
flyctl deploy
```

**注意**：超过免费额度可能产生费用，请查看 [Fly.io 价格](https://fly.io/docs/about/pricing/)。

### 问题 4：无法访问应用

**症状**：访问 `https://your-app-name.fly.dev` 返回错误

**解决方法**：

```bash
# 检查应用是否运行
flyctl status

# 检查证书状态
flyctl certs check your-app-name.fly.dev

# 查看详细信息
flyctl info
```

### 问题 5：环境变量未生效

**症状**：机器人使用了错误的配置

**解决方法**：

```bash
# 检查已设置的 Secrets
flyctl secrets list

# 重新设置 Secret
flyctl secrets set WEBHOOK_URL=https://your-app-name.fly.dev

# 应用会自动重启以使用新的 Secrets
```

---

## 📊 性能优化建议

### 1. 内存优化

Fly.io 免费额度提供 256MB 内存，优化配置：

```ini
# config.ini
[SEARCH]
ANALYZER = simple  # 节省 ~140MB

[DB]
CACHE_SIZE_KB = 1024  # 适度缓存
```

### 2. 自动缩容配置

在 `fly.toml` 中配置自动缩容，节省资源：

```toml
[http_service]
  auto_stop_machines = true    # 无流量时自动停止
  auto_start_machines = true   # 有请求时自动启动
  min_machines_running = 0     # 最少运行 0 个实例
```

### 3. 区域选择

选择离用户最近的区域以降低延迟：

```bash
# 查看可用区域
flyctl platform regions

# 常用区域：
# hkg - 香港
# nrt - 东京
# sjc - 美国加州
# fra - 德国法兰克福
```

---

## 🔄 更新和维护

### 更新代码

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新部署
flyctl deploy

# 3. 查看部署状态
flyctl status
```

### 查看日志

```bash
# 实时日志
flyctl logs

# 查看最近 100 行
flyctl logs -n 100

# 持续监控
flyctl logs -f
```

### 数据备份

```bash
# 连接到应用容器
flyctl ssh console

# 备份数据库
cd /app/data
tar -czf backup.tar.gz submissions.db

# 退出容器
exit

# 下载备份（需要配置 SFTP 或使用 Fly.io Volumes）
```

### 扩容/缩容

```bash
# 增加实例数量（高可用）
flyctl scale count 2

# 升级内存
flyctl scale memory 512

# 查看当前配置
flyctl scale show
```


---

## 📚 相关文档

- [主文档 - README.md](../README.md)
- [Webhook 模式完整指南](WEBHOOK_MODE.md)
- [部署指南 - DEPLOYMENT.md](../DEPLOYMENT.md)
- [内存优化指南 - MEMORY_USAGE.md](../MEMORY_USAGE.md)
- [Fly.io 官方文档](https://fly.io/docs/)

---

## 💬 获取帮助

如遇到问题：

1. **检查文档**：先查看本指南和 Fly.io 官方文档
2. **查看日志**：`flyctl logs` 通常包含详细错误信息
3. **Fly.io 社区**：[Fly.io Community](https://community.fly.io/)
4. **提交 Issue**：在 [GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues) 提问

---

**最后更新**：2025-12-02  
**适用版本**：TeleSubmit v2.1+  
**测试环境**：Fly.io Free Tier (256MB RAM)

**部署成功标志**：
- ✅ `flyctl status` 显示 running
- ✅ 健康检查返回 OK
- ✅ Webhook 信息正确
- ✅ 机器人响应正常（< 1 秒）
- ✅ 完全免费运行 🎉
