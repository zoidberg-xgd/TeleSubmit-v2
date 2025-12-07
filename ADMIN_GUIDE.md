# TeleSubmit v2 管理员指南

## 目录
1. [配置机器人所有者](#配置机器人所有者)
2. [管理员命令列表](#管理员命令列表)
3. [管理功能说明](#管理功能说明)
4. [黑名单管理](#黑名单管理)
5. [统计数据查看](#统计数据查看)
6. [内容管理](#内容管理)
7. [系统维护](#系统维护)
8. [常见问题](#常见问题)

---

## 配置机器人所有者

### 1. 获取您的 Telegram User ID

有三种方法获取您的 User ID：

**方法一：使用 @userinfobot**
1. 在 Telegram 中搜索 `@userinfobot`
2. 发送任意消息
3. 机器人会回复您的 User ID

**方法二：使用 @getmyid_bot**
1. 在 Telegram 中搜索 `@getmyid_bot`
2. 点击 START
3. 查看 "Your user ID" 字段

**方法三：使用机器人的 `/debug` 命令**
1. 启动您的机器人
2. 发送 `/debug` 命令
3. 查看 "您的用户ID" 字段

### 2. 配置 OWNER_ID

编辑 `config.ini` 文件：

```ini
[BOT]
# 机器人所有者的 Telegram User ID
OWNER_ID = 你的用户ID数字
```

或者使用环境变量（适用于 Docker 部署）：

```bash
export OWNER_ID=你的用户ID数字
```

**示例**：
```ini
OWNER_ID = 5073758941
```

### 3. 验证配置

重启机器人后，发送 `/debug` 命令检查：

```
🔍 调试信息

👤 您的用户ID: 5073758941
🤖 机器人所有者ID: 5073758941
✅ 您是所有者: True
```

---

## 管理员命令列表

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/start` | 启动机器人 | `/start` |
| `/help` | 查看帮助信息 | `/help` |
| `/debug` | 查看系统调试信息 | `/debug` |

### 黑名单管理命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/blacklist_add <user_id> [原因]` | 添加用户到黑名单 | `/blacklist_add 123456789 发送垃圾内容` |
| `/blacklist_remove <user_id>` | 从黑名单移除用户 | `/blacklist_remove 123456789` |
| `/blacklist_list` | 查看黑名单列表 | `/blacklist_list` |

### 统计命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/hot` | 查看热门投稿 | `/hot` |
| `/mystats` | 查看个人统计 | `/mystats` |

### 搜索命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/search <关键词>` | 全文搜索 | `/search Python` |
| `/search #标签` | 标签搜索 | `/search #编程` |
| `/tags [数量]` | 查看标签云 | `/tags 10` |
| `/myposts` | 查看我的投稿 | `/myposts` |
| `/searchuser <user_id>` | 搜索指定用户的投稿 | `/searchuser 123456789` |

### 系统命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/settings` | 查看机器人设置 | `/settings` |
| `/cancel` | 取消当前操作 | `/cancel` |

---

## 管理功能说明

当前版本不再提供内置“管理面板”按钮式界面。请直接使用上方命令完成管理任务（黑名单、统计、搜索等）。

---

## 黑名单管理

- 通过 `/blacklist_add`、`/blacklist_remove`、`/blacklist_list` 管理黑名单。
- 黑名单用户将无法使用机器人投稿或交互。

---

## 统计数据查看

- 使用 `/hot` 查看站内热门帖子。
- 使用 `/mystats` 查看个人投稿统计。
- 常见问题与故障排查请参阅 [统计功能常见问题](STATS_FAQ.md)。

---

## 内容管理

- 使用 `/myposts` 查看个人投稿并结合频道手动操作。
- 需要删除帖子记录时，请参考 `DELETE_POST_GUIDE.md`。

---

## 系统维护

- 数据库优化参见 `optimize_database.py` 与 `DEPLOYMENT.md` 的定时任务建议。
- 搜索索引维护参见 `utils/index_manager.py` 与迁移脚本。

---

## 常见问题

- 没有“管理面板”入口了怎么办？
  - 直接使用上方命令即可，功能等价且更稳定。
- 权限相关？
  - `/debug` 会给出“您是所有者: True/False”以便确认权限。

