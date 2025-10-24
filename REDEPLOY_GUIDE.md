# 文件名搜索功能 - 重新部署指南

## 🚀 快速重新部署（推荐）

### 方法一：一键升级脚本

```bash
# 1. 停止机器人
./restart.sh --stop

# 2. 拉取最新代码
git pull origin main

# 3. 运行数据库迁移
python3 migrate_add_filename.py

# 4. 重建搜索索引
echo "y" | python3 migrate_to_search.py --clear

# 5. 重启机器人
./restart.sh
```

### 方法二：后台运行模式

如果您使用 nohup 或 screen 运行：

```bash
# 1. 停止机器人
pkill -f "python.*main.py"

# 2. 更新代码
git pull origin main

# 3. 数据库迁移
python3 migrate_add_filename.py

# 4. 重建索引
echo "y" | python3 migrate_to_search.py --clear

# 5. 后台启动
nohup python3 -u main.py > logs/bot.log 2>&1 &

# 或使用 screen
screen -S telesubmit
python3 -u main.py
# 按 Ctrl+A+D 退出 screen
```

## 📋 详细步骤说明

### 第一步：停止现有机器人

**使用 restart.sh（推荐）：**
```bash
./restart.sh --stop
```

**手动停止：**
```bash
# 查找进程
ps aux | grep "python.*main.py"

# 停止进程（替换 <PID> 为实际进程号）
kill <PID>

# 或强制停止
kill -9 <PID>
```

**验证已停止：**
```bash
ps aux | grep "python.*main.py"
# 应该只显示 grep 命令本身
```

### 第二步：更新代码

```bash
# 查看当前状态
git status

# 拉取最新代码
git pull origin main

# 验证更新成功
git log -1 --oneline
# 应该显示：feat: 添加文件名搜索功能
```

**如果有本地修改冲突：**
```bash
# 暂存本地修改
git stash

# 拉取最新代码
git pull origin main

# 恢复本地修改
git stash pop
```

### 第三步：数据库迁移

```bash
# 运行迁移脚本
python3 migrate_add_filename.py

# 预期输出示例：
# ✅ 数据库迁移完成
# 📊 已为 published_posts 表添加 filename 字段
# 💡 注意：历史数据的 filename 字段为 NULL（这是正常的）
```

**验证迁移成功：**
```bash
# 检查数据库结构
sqlite3 data/submissions.db "PRAGMA table_info(published_posts);" | grep filename
# 应该看到 filename 字段
```

### 第四步：重建搜索索引

```bash
# 自动确认方式（推荐）
echo "y" | python3 migrate_to_search.py --clear

# 或交互式运行
python3 migrate_to_search.py --clear
# 提示时输入 y 确认
```

**预期输出：**
```
🔍 正在从数据库加载投稿...
✅ 成功加载 X 条投稿
📊 索引重建进度: 100%
✅ 搜索索引重建成功！
```

**验证索引成功：**
```bash
# 检查索引目录
ls -la data/search_index/
# 应该看到多个索引文件
```

### 第五步：重启机器人

**使用 restart.sh（推荐）：**
```bash
./restart.sh
```

**后台运行模式：**
```bash
# 使用 nohup
nohup python3 -u main.py > logs/bot.log 2>&1 &

# 查看日志
tail -f logs/bot.log
```

**使用 screen：**
```bash
# 创建新 screen 会话
screen -S telesubmit

# 启动机器人
python3 -u main.py

# 按 Ctrl+A+D 退出（机器人继续运行）
# 重新连接：screen -r telesubmit
```

**使用 systemd（Linux 服务器）：**
```bash
# 重启服务
sudo systemctl restart telesubmit

# 查看状态
sudo systemctl status telesubmit

# 查看日志
sudo journalctl -u telesubmit -f
```

## ✅ 验证部署成功

### 1. 检查机器人状态

```bash
# 检查进程
ps aux | grep "python.*main.py"
# 应该看到运行中的进程

# 查看日志（如果使用日志文件）
tail -f logs/bot.log
```

### 2. 在 Telegram 中测试

**测试文件名搜索：**
```
1. 发送 /submit 开始新投稿
2. 上传一个文档（例如：Python教程.txt）
3. 填写标题、简介、标签
4. 确认发布
5. 发送 /search Python教程
6. 应该能搜索到刚才的投稿
```

**测试搜索帮助：**
```
/search_help
# 应该看到文件名搜索的说明
```

### 3. 检查日志

查看机器人启动时的日志：
```
✅ 搜索引擎初始化成功
✅ 数据库连接成功
✅ Bot 启动成功
```

## ⚠️ 常见问题排查

### 问题 1：迁移脚本报错

**症状：**
```
Error: no such column: filename
```

**解决方案：**
```bash
# 重新运行迁移
python3 migrate_add_filename.py

# 如果仍然失败，检查数据库
sqlite3 data/submissions.db "PRAGMA table_info(published_posts);"
```

### 问题 2：搜索索引重建失败

**症状：**
```
Error: whoosh module not found
```

**解决方案：**
```bash
# 安装搜索引擎依赖
pip3 install whoosh jieba

# 重新运行索引重建
echo "y" | python3 migrate_to_search.py --clear
```

### 问题 3：机器人启动失败

**症状：**
```
ModuleNotFoundError: No module named 'whoosh'
```

**解决方案：**
```bash
# 重新安装依赖
pip3 install -r requirements.txt

# 或单独安装
pip3 install whoosh jieba
```

### 问题 4：搜索不到文件名

**症状：**
- 新上传的文档无法通过文件名搜索

**排查步骤：**
```bash
# 1. 检查数据库
sqlite3 data/submissions.db "SELECT id, title, filename FROM published_posts ORDER BY id DESC LIMIT 5;"
# 新投稿的 filename 字段应该有值

# 2. 检查搜索索引
python3 -c "
from whoosh.index import open_dir
ix = open_dir('data/search_index')
with ix.searcher() as searcher:
    print(f'索引文档数: {searcher.doc_count_all()}')
"

# 3. 重建索引
echo "y" | python3 migrate_to_search.py --clear
```

### 问题 5：端口占用

**症状：**
```
Address already in use
```

**解决方案：**
```bash
# 查找占用进程
lsof -i :8080  # 替换为实际端口

# 停止旧进程
./restart.sh --stop

# 或手动停止
pkill -f "python.*main.py"
```

## 🔧 高级选项

### 备份数据

在重新部署前备份重要数据：

```bash
# 备份数据库
cp data/submissions.db data/submissions.db.backup.$(date +%Y%m%d_%H%M%S)

# 备份搜索索引
cp -r data/search_index data/search_index.backup.$(date +%Y%m%d_%H%M%S)

# 备份配置文件
cp config.ini config.ini.backup.$(date +%Y%m%d_%H%M%S)
```

### 回滚到旧版本

如果遇到问题需要回滚：

```bash
# 1. 停止机器人
./restart.sh --stop

# 2. 回滚代码
git log --oneline -10  # 查看提交历史
git checkout <previous_commit_hash>

# 3. 恢复数据库备份
cp data/submissions.db.backup.<timestamp> data/submissions.db

# 4. 重建索引
echo "y" | python3 migrate_to_search.py --clear

# 5. 重启
./restart.sh
```

### 生产环境部署建议

**使用 systemd（推荐）：**

创建服务文件 `/etc/systemd/system/telesubmit.service`：
```ini
[Unit]
Description=TeleSubmit v2 Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/TeleSubmit-v2
ExecStart=/usr/bin/python3 -u main.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/telesubmit/bot.log
StandardError=append:/var/log/telesubmit/error.log

[Install]
WantedBy=multi-user.target
```

部署命令：
```bash
# 重载服务配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start telesubmit

# 设置开机自启
sudo systemctl enable telesubmit

# 查看状态
sudo systemctl status telesubmit
```

## 📊 部署检查清单

- [ ] 机器人已停止
- [ ] 代码已更新（git pull）
- [ ] 数据库已迁移（migrate_add_filename.py）
- [ ] 搜索索引已重建（migrate_to_search.py --clear）
- [ ] 依赖已安装（requirements.txt）
- [ ] 机器人已重启
- [ ] 测试文件名搜索功能
- [ ] 检查日志无错误
- [ ] 备份已创建

## 🎉 部署完成

恭喜！您已成功部署文件名搜索功能。现在用户可以通过文件名搜索投稿了！

如有任何问题，请查看：
- [详细升级指南](FILENAME_SEARCH_UPGRADE.md)
- [快速升级指南](UPGRADE_QUICKSTART.md)
- [变更日志](CHANGELOG.md)

