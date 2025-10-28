# TeleSubmit v2 脚本使用指南

本文档介绍项目中所有管理脚本的功能和使用方法。

## 脚本概览

| 脚本 | 用途 | 使用频率 |
|------|------|----------|
| `quickstart.sh` | 快速启动向导 | 首次部署 |
| `install.sh` | 一键安装向导 | 首次部署 |
| `deploy.sh` | Docker 部署 | 首次部署 |
| `start.sh` | 启动机器人 | 日常使用 |
| `restart.sh` | 重启机器人 | 日常使用 ⭐ |
| `update.sh` | 拉取更新 | 定期维护 |
| `upgrade.sh` | 功能升级 | 版本升级 |
| `uninstall.sh` | 卸载程序 | 移除服务 |

> **v2.1+ 新特性**: 修改配置后使用 `restart.sh` 即可自动完成分词器切换和索引重建！

## 首次部署

### 1. quickstart.sh - 快速启动向导

**适合人群**：所有用户，特别是新手

```bash
./quickstart.sh
```

**功能特点：**
- 自动检测系统环境（操作系统、Python、Docker、Git）
- 显示环境检测结果和版本信息
- 智能推荐最适合的部署方式
- 提供 4 种部署选项：
  1. 一键安装（完整向导）
  2. 直接启动（已配置环境）
  3. Docker 部署（需要 Docker）
  4. 仅检查配置

**使用流程：**
```
运行脚本 → 查看环境检测 → 选择部署方式 → 自动执行
```

### 2. install.sh - 一键安装向导

**适合人群**：首次部署的用户

```bash
./install.sh
```

**完整流程：**
1. 检测操作系统（Linux/macOS）
2. 检查 Python 版本（>= 3.9）
3. 检查并安装 pip3
4. 创建必要目录（data、logs、backups）
5. 安装 Python 依赖
6. **配置向导**（交互式输入）
   - Bot Token（必填）
   - 频道 ID（必填）
   - 管理员 ID（必填）
   - **运行模式选择**（Polling/Webhook）
   - Webhook URL（Webhook 模式时）
7. 验证配置文件
8. 初始化数据库
9. 询问是否立即启动

**配置示例：**
```
Bot Token (从 @BotFather 获取): 123456:ABC-DEF...
频道 ID (如 @mychannel 或 -100123456789): @mychannel
管理员 ID (向 @userinfobot 发消息获取): 123456789

选择运行模式：
  1) Polling 模式 (轮询) - 推荐用于本地开发和测试
  2) Webhook 模式 - 推荐用于生产环境和云服务器
请选择 (1/2) [默认: 1]: 2

Webhook URL (可留空稍后配置): https://your-domain.com
```

### 3. deploy.sh - Docker 部署

**适合人群**：生产环境、需要容器隔离

```bash
# 首次部署
./deploy.sh

# 强制重新构建镜像
./deploy.sh --rebuild
```

**功能特点：**
- 检查 Docker 和 Docker Compose
- 自动构建镜像
- 自动重启策略
- 数据持久化（挂载 data、logs、backups）
- 网络隔离

**Docker 管理命令：**
```bash
docker-compose ps                # 查看容器状态
docker-compose logs -f           # 查看容器日志
docker-compose down              # 停止容器
docker-compose restart           # 重启容器
```

## 日常管理

### 4. start.sh - 启动机器人

**使用场景**：已配置环境，需要启动机器人

```bash
./start.sh
```

**执行流程：**
1. 检查 Python 版本
2. 检查配置文件（config.ini）
3. 检查依赖包
4. 创建必要目录
5. 检查是否已运行
6. 后台启动机器人（nohup）
7. 验证启动成功

**输出日志：**
- 标准输出/错误：`logs/bot.log`
- 进程 ID：启动时显示

### 5. restart.sh - 重启机器人

**使用场景**：修改配置后、更新代码后

```bash
# 正常重启
./restart.sh

# 仅停止，不启动
./restart.sh --stop
```

**执行流程：**
1. 停止现有进程（pkill -f "python.*main.py"）
2. 等待 2 秒
3. 强制停止（如果还在运行）
4. 启动新进程（除非 --stop）

**停止方式：**
- 优先使用 SIGTERM（正常退出）
- 2 秒后使用 SIGKILL（强制终止）

### 6. update.sh - 更新代码

**使用场景**：拉取最新代码、修复 Bug、获取新功能

```bash
./update.sh
```

**完整流程：**
1. 检查 Git 环境
2. 备份配置和数据
3. 检查本地修改（询问是否继续）
4. 拉取最新代码（git pull）
5. 更新 Python 依赖
6. 运行数据库迁移
7. 重启机器人
8. 显示更新日志

**备份位置：**
```
backups/update_YYYYMMDD_HHMMSS/
├── config.ini
└── data/
```

**注意事项：**
- 会提示本地修改（如果有）
- 自动合并代码（可能需要解决冲突）
- 保留本地配置文件

### 7. upgrade.sh - 功能升级

**使用场景**：大版本升级、数据迁移、功能更新

```bash
./upgrade.sh
```

**升级流程：**
1. 创建完整备份
2. 更新 Python 依赖
3. 检查数据库结构
4. 检查搜索索引
5. 运行搜索迁移（如需要）
6. 清理过期数据
7. 优化搜索索引
8. 验证升级结果
9. 重启机器人
10. 显示升级摘要

**与 update.sh 的区别：**

| 功能 | update.sh | upgrade.sh |
|------|-----------|------------|
| 拉取代码 | 是 | - |
| 更新依赖 | 是 | 是 |
| 数据迁移 | 基础 | 完整 |
| 索引优化 | - | 是 |
| 数据清理 | - | 是 |
| 升级摘要 | 简单 | 详细 |

**适用情况：**
- 首次启用搜索功能
- 大版本更新（如 v1 → v2）
- 数据库结构变更
- 搜索索引重建

## 卸载

### 8. uninstall.sh - 卸载脚本

**使用场景**：完全移除、重新部署、更换服务器

```bash
./uninstall.sh
```

**三种模式：**

#### 模式 1：仅停止服务
- 停止机器人进程
- 停止 Docker 容器（如果有）
- **保留所有数据和配置**
- 可随时使用 `./start.sh` 恢复

#### 模式 2：备份并卸载（推荐）
- 停止服务
- **创建完整备份**
- 删除所有文件
- 询问是否卸载依赖

**备份内容：**
```
backups/uninstall_YYYYMMDD_HHMMSS/
├── config.ini          # 配置文件
├── data/               # 数据目录
├── logs/               # 日志文件
└── README.txt          # 恢复说明
```

#### 模式 3：完全删除
- 停止服务
- 删除所有文件（不备份）
- 询问是否卸载依赖
- **不可恢复，谨慎使用**

**恢复方法：**
```bash
# 1. 重新克隆仓库
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2

# 2. 复制备份
cp -r backups/uninstall_*/config.ini .
cp -r backups/uninstall_*/data .

# 3. 启动
./start.sh
```

## 脚本对比

### 首次部署选择

```
是否确定部署方式？
├─ 否 → quickstart.sh（向导帮你选）
└─ 是
   ├─ 需要完整向导 → install.sh
   ├─ 已有 Docker → deploy.sh
   └─ 已配置环境 → start.sh
```

### 更新选择

```
需要更新吗？
├─ 拉取代码 → update.sh
├─ 大版本升级 → upgrade.sh
└─ 修改配置 → 手动编辑 + restart.sh
```

## 常见场景

### 场景 1：首次部署（完全新手）
```bash
./quickstart.sh
# 跟随向导选择 → 自动完成
```

### 场景 2：修改配置后重启
```bash
nano config.ini        # 编辑配置
./restart.sh           # 重启生效
```

### 场景 3：更新到最新版本
```bash
./update.sh            # 自动备份、拉取、重启
```

### 场景 4：首次启用搜索功能
```bash
./upgrade.sh           # 完整升级流程
```

### 场景 5：迁移到新服务器
```bash
# 旧服务器
./uninstall.sh         # 选择 "备份并卸载"
scp -r backups/uninstall_* user@new-server:~/

# 新服务器
git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git
cd TeleSubmit-v2
cp -r ~/uninstall_*/config.ini .
cp -r ~/uninstall_*/data .
./start.sh
```

### 场景 6：Docker 环境重新部署
```bash
./deploy.sh --rebuild  # 强制重建镜像
```

### 场景 7：切换分词器（v2.1+）⭐

**从 simple 切换到 jieba（高质量中文分词）**:
```bash
# 1. 编辑 requirements.txt
# 取消注释: jieba>=0.42.1
nano requirements.txt

# 2. 安装 jieba
pip install jieba>=0.42.1

# 3. 修改配置
nano config.ini
# 设置: [SEARCH] ANALYZER = jieba

# 4. 重启（自动完成索引重建）
./restart.sh
```

**从 jieba 切换到 simple（节省 ~140MB 内存）**:
```bash
# 1. 修改配置
nano config.ini
# 设置: [SEARCH] ANALYZER = simple

# 2. 重启（自动完成索引重建）
./restart.sh

# 3. 可选：卸载 jieba 节省空间
pip uninstall jieba -y
```

**自动适配说明**:
- ✅ v2.1+ 版本会自动检测分词器变化
- ✅ 自动备份旧索引到 `data/search_index.backup`
- ✅ 自动创建新索引并重新索引所有帖子
- ✅ 失败时自动回滚，不影响其他功能

详见 [内存优化指南](MEMORY_USAGE.md)

## 脚本维护

所有脚本都包含：
- 颜色化输出（蓝色=信息，绿色=成功，黄色=警告，红色=错误）
- 错误处理（set -e）
- 日志记录
- 用户友好的提示信息

**查看脚本源码：**
```bash
cat install.sh         # 查看安装脚本
head -50 quickstart.sh # 查看前 50 行
```

**检查脚本语法：**
```bash
bash -n install.sh     # 语法检查
```

## 注意事项

1. **权限问题**：
   ```bash
   chmod +x *.sh       # 添加可执行权限
   ```

2. **配置备份**：
   - update.sh 和 upgrade.sh 会自动备份
   - 手动备份：`cp config.ini config.ini.backup`

3. **Docker 用户**：
   - 使用 `deploy.sh` 而不是 `start.sh`
   - 日志查看：`docker-compose logs -f`

4. **多个实例**：
   - 避免同时运行多个机器人实例
   - restart.sh 会自动检测并停止旧进程

5. **网络问题**：
   - update.sh 需要访问 GitHub
   - 可能需要配置代理或使用镜像

## 故障排查

**脚本执行失败？**
```bash
# 查看详细错误
bash -x ./install.sh   # 调试模式

# 检查依赖
python3 --version      # 检查 Python
docker --version       # 检查 Docker
```

**权限被拒绝？**
```bash
chmod +x *.sh          # 添加执行权限
```

**找不到脚本？**
```bash
ls -la *.sh            # 列出所有脚本
pwd                    # 确认当前目录
```

---

## 相关文档

- [README](README.md) - 项目介绍和快速开始
- [部署指南](DEPLOYMENT.md) - 部署步骤和故障排查
- [管理员指南](ADMIN_GUIDE.md) - 管理功能和系统维护
- [索引管理器](INDEX_MANAGER_README.md) - 搜索索引管理
- [内存占用说明](MEMORY_USAGE.md) - 内存使用分析
- [更新日志](CHANGELOG.md) - 版本历史

---

**获取帮助：**
- 问题反馈：[GitHub Issues](https://github.com/zoidberg-xgd/TeleSubmit-v2/issues)
- 功能建议：[GitHub Discussions](https://github.com/zoidberg-xgd/TeleSubmit-v2/discussions)

