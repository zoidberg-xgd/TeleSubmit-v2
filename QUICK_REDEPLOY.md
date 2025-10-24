# 🚀 快速重新部署

## 一键升级（最简单）

```bash
./upgrade.sh
```

这个脚本会自动完成：
- ✅ 备份数据
- ✅ 停止机器人
- ✅ 更新代码
- ✅ 数据库迁移
- ✅ 重建索引
- ✅ 启动机器人

---

## 手动升级（分步执行）

### 1️⃣ 停止机器人
```bash
./restart.sh --stop
```

### 2️⃣ 更新代码
```bash
git pull origin main
```

### 3️⃣ 数据库迁移
```bash
python3 migrate_add_filename.py
```

### 4️⃣ 重建索引
```bash
echo "y" | python3 migrate_to_search.py --clear
```

### 5️⃣ 重启机器人
```bash
./restart.sh
```

---

## 后台运行模式

### 使用 nohup
```bash
# 停止
pkill -f "python.*main.py"

# 更新
git pull && python3 migrate_add_filename.py && echo "y" | python3 migrate_to_search.py --clear

# 启动
nohup python3 -u main.py > logs/bot.log 2>&1 &

# 查看日志
tail -f logs/bot.log
```

### 使用 screen
```bash
# 停止现有会话
screen -X -S telesubmit quit

# 更新
git pull && python3 migrate_add_filename.py && echo "y" | python3 migrate_to_search.py --clear

# 启动新会话
screen -dmS telesubmit python3 -u main.py

# 查看会话
screen -r telesubmit
```

### 使用 systemd
```bash
# 更新代码
sudo -u bot_user git -C /path/to/TeleSubmit-v2 pull

# 运行迁移
sudo -u bot_user python3 /path/to/TeleSubmit-v2/migrate_add_filename.py
sudo -u bot_user bash -c "echo 'y' | python3 /path/to/TeleSubmit-v2/migrate_to_search.py --clear"

# 重启服务
sudo systemctl restart telesubmit

# 查看状态
sudo systemctl status telesubmit
```

---

## 验证部署

### 检查进程
```bash
ps aux | grep "python.*main.py"
```

### 测试搜索
在 Telegram 中：
1. 上传一个文档（例如：`测试文档.txt`）
2. 发送 `/search 测试文档`
3. 应该能搜索到刚才的投稿

### 查看日志
```bash
tail -f logs/bot.log
# 应该看到：✅ 搜索引擎初始化成功
```

---

## 回滚（如遇问题）

```bash
# 停止机器人
./restart.sh --stop

# 回滚代码
git checkout <previous_commit>

# 恢复备份
cp data/submissions.db.backup_<timestamp> data/submissions.db

# 重建索引
echo "y" | python3 migrate_to_search.py --clear

# 重启
./restart.sh
```

---

## 常见问题

### 问题：`whoosh module not found`
```bash
pip3 install whoosh jieba
```

### 问题：搜索不到文件名
```bash
echo "y" | python3 migrate_to_search.py --clear
./restart.sh
```

### 问题：端口占用
```bash
pkill -f "python.*main.py"
./restart.sh
```

---

## 📚 详细文档

- 📋 [完整重新部署指南](REDEPLOY_GUIDE.md)
- ⚡ [快速升级指南](UPGRADE_QUICKSTART.md)
- 🔧 [详细升级指南](FILENAME_SEARCH_UPGRADE.md)
- 📝 [变更日志](CHANGELOG.md)

---

**💡 提示：推荐使用 `./upgrade.sh` 一键升级！**

