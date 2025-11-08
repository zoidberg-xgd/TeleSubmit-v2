# 频道消息监听功能测试指南

## ✅ 功能状态

- **Bot 状态**: ✅ 正在运行 (PID: 94791)
- **监听器状态**: ✅ 已注册
- **运行模式**: Polling 模式
- **监听频道**: @xgdTest

## 🧪 测试步骤

### 1. 确认 Bot 正在运行

```bash
# 检查进程
ps aux | grep "python.*main.py" | grep -v grep

# 查看日志
tail -f logs/bot.log
```

### 2. 在频道中发布测试消息

在 Telegram 频道 `@xgdTest` 中发布一条新消息，例如：

```
测试消息 #测试 #频道监听

这是一条测试消息，用于验证频道消息监听功能。
```

### 3. 验证消息是否被记录

#### 方法1: 查看实时日志

```bash
tail -f logs/bot.log | grep -E "频道消息|channel_post|已保存频道"
```

当频道有新消息时，应该看到类似日志：
```
收到频道消息: <message_id>
已保存频道消息 <message_id> (post_id: <post_id>) 到数据库
已添加频道消息 <message_id> (post_id: <post_id>) 到搜索索引
频道消息 <message_id> 处理完成
```

#### 方法2: 检查数据库

```bash
python3 -c "
import asyncio
from database.db_manager import get_db

async def check():
    async with get_db() as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT message_id, title, tags, publish_time FROM published_posts WHERE username = \"channel\" ORDER BY publish_time DESC LIMIT 5')
        rows = await cursor.fetchall()
        print(f'找到 {len(rows)} 条频道消息:')
        for row in rows:
            print(f'  消息ID: {row[0]}, 标题: {row[1] or \"无\"}, 标签: {row[2] or \"无\"}')

asyncio.run(check())
"
```

#### 方法3: 使用测试脚本

```bash
python3 test_channel_listener_live.py
```

## 📋 功能特性

### 自动提取信息

频道消息监听器会自动从消息中提取：

1. **标签**: 从文本中提取 `#标签` 格式的标签
2. **标题**: 智能提取标题（支持多种格式）
3. **链接**: 提取 HTTP/HTTPS 链接
4. **说明**: 提取消息正文（去除标签和链接后）
5. **媒体**: 自动识别照片、视频、文档等
6. **文件名**: 从文档中提取文件名

### 数据验证

- 自动验证和规范化数据
- 处理不规范的消息格式
- 防止数据库溢出（字段长度限制）
- 自动去重（避免重复记录）

### 搜索索引

- 自动添加到搜索索引
- 支持全文搜索
- 支持标签搜索

## 🔍 故障排查

### 问题1: 频道消息没有被记录

**可能原因**:
1. Bot 没有监听频道的权限
2. 频道ID配置错误
3. 消息格式无法解析

**解决方法**:
1. 检查 `config.ini` 中的 `CHANNEL_ID` 是否正确
2. 确认 Bot 是频道管理员或有权限查看频道消息
3. 查看日志中的错误信息

### 问题2: 数据不完整

**可能原因**:
1. 消息格式不规范
2. 字段长度超限

**解决方法**:
- 查看日志中的警告信息
- 系统会自动使用默认值填充缺失字段

## 📊 当前状态

运行以下命令查看当前状态：

```bash
# 查看 Bot 进程
ps aux | grep "python.*main.py" | grep -v grep

# 查看最新日志
tail -n 50 logs/bot.log

# 检查数据库中的频道消息
python3 -c "
import asyncio
from database.db_manager import get_db
async def check():
    async with get_db() as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT COUNT(*) FROM published_posts WHERE username = \"channel\"')
        count = await cursor.fetchone()
        print(f'频道消息总数: {count[0]}')
asyncio.run(check())
"
```

