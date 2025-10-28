# TeleSubmit v2 内存占用说明

## 🚀 快速优化

### 一键优化脚本（推荐）

```bash
# 应用推荐的内存优化配置
./optimize_memory.sh
```

**效果**: 内存从 ~250 MB 降至 ~80-120 MB（降低 60-84%）

### 模式切换

在不同配置之间快速切换：

```bash
./switch_mode.sh minimal      # 极致省内存 (~80-120 MB)
./switch_mode.sh balanced     # 均衡模式 (~150-200 MB) 推荐
./switch_mode.sh performance  # 性能优先 (~200-350 MB)
./switch_mode.sh nosearch     # 禁用搜索 (~60-100 MB)
```

查看所有选项：`./switch_mode.sh --help`

---

## 快速回答

### 🎯 典型内存占用

| 场景 | 内存占用 | 推荐配置 |
|-----|---------|---------|
| **小型频道** (<1000 帖子) | ~150 MB | 256 MB |
| **中型频道** (1000-10000 帖子) | ~200-400 MB | 512 MB |
| **大型频道** (10000-50000 帖子) | ~400-700 MB | 1 GB |
| **超大频道** (>50000 帖子) | ~700+ MB | 1-2 GB |

### 🚀 最小要求
- **内存**: 256 MB（包含搜索功能）
- **磁盘**: 100 MB（代码 + 依赖 + 小型数据库）

---

## 详细分析

### 1️⃣ 基础内存占用

```
┌─────────────────────────────────────────┐
│ 组件                    │ 内存占用      │
├─────────────────────────────────────────┤
│ Python 解释器           │ ~16 MB        │
│ python-telegram-bot     │ ~29 MB        │
│ Whoosh 搜索引擎          │ ~0.5 MB       │
│ jieba 中文分词           │ ~22 MB        │
│ aiosqlite 异步数据库     │ ~0.5 MB       │
│ 其他依赖                │ ~2 MB         │
├─────────────────────────────────────────┤
│ 小计（静态加载）         │ ~70 MB        │
└─────────────────────────────────────────┘
```

### 2️⃣ 运行时内存占用

```
┌─────────────────────────────────────────┐
│ 组件                    │ 内存占用      │
├─────────────────────────────────────────┤
│ Bot 框架和连接           │ ~50 MB        │
│ 对话状态管理             │ ~10 MB        │
│ 消息缓存                │ ~20 MB        │
├─────────────────────────────────────────┤
│ 小计（运行时开销）       │ ~80 MB        │
└─────────────────────────────────────────┘
```

### 3️⃣ 搜索索引内存占用

搜索索引的内存占用取决于帖子数量和内容大小：

```python
# 估算公式
索引内存 ≈ 索引文件大小 × 25%

# 典型数据
- 100 帖子   → 索引 ~500 KB   → 内存 ~0.1 MB
- 1000 帖子  → 索引 ~5 MB     → 内存 ~1.2 MB
- 10000 帖子 → 索引 ~50 MB    → 内存 ~12 MB
- 50000 帖子 → 索引 ~250 MB   → 内存 ~60 MB
```

> 💡 **注意**: Whoosh 采用磁盘存储 + 按需加载的策略，不会将整个索引加载到内存

### 4️⃣ 数据库内存占用

SQLite 数据库采用按需加载：

```python
- 1000 帖子   → 数据库 ~1 MB    → 内存 ~2 MB
- 10000 帖子  → 数据库 ~10 MB   → 内存 ~20 MB
- 50000 帖子  → 数据库 ~50 MB   → 内存 ~100 MB
```

---

## 📈 内存占用计算

### 完整公式

```python
总内存 = 基础内存 + 运行时内存 + 索引内存 + 数据库内存

基础内存 = 70 MB（固定）
运行时内存 = 80 MB（固定）
索引内存 = 索引文件大小 × 0.25
数据库内存 = 数据库文件大小 × 2
```

### 示例计算

#### 场景 1: 小型频道 (500 帖子)

```
基础内存:   70 MB
运行时:     80 MB
索引内存:   2.5 MB (10 MB 索引 × 0.25)
数据库:     1 MB (0.5 MB DB × 2)
─────────────────
总计:      ~153 MB

推荐配置:   256 MB
```

#### 场景 2: 中型频道 (5000 帖子)

```
基础内存:   70 MB
运行时:     80 MB
索引内存:   7.5 MB (30 MB 索引 × 0.25)
数据库:     10 MB (5 MB DB × 2)
─────────────────
总计:      ~167 MB

推荐配置:   256-512 MB
```

#### 场景 3: 大型频道 (20000 帖子)

```
基础内存:   70 MB
运行时:     80 MB
索引内存:   25 MB (100 MB 索引 × 0.25)
数据库:     40 MB (20 MB DB × 2)
─────────────────
总计:      ~215 MB

推荐配置:   512 MB
```

#### 场景 4: 超大频道 (100000 帖子)

```
基础内存:   70 MB
运行时:     80 MB
索引内存:   125 MB (500 MB 索引 × 0.25)
数据库:     200 MB (100 MB DB × 2)
─────────────────
总计:      ~475 MB

推荐配置:   1 GB
```

---

## 🔧 内存优化建议

### 1. 使用轻量分词器（节省 ~140+ MB）⭐ 推荐

**配置**: `config.ini` → `[SEARCH] ANALYZER = simple`

```ini
[SEARCH]
ANALYZER = simple  # 从 jieba 改为 simple
```

**节省内存**:
- jieba 词典加载: ~140 MB（导入时）
- **总计**: 导入阶段降低 **83.6%** 内存

**注意**: 重建索引后生效
```bash
python3 utils/index_manager.py rebuild
```

### 2. 关闭搜索高亮（节省少量内存）

**配置**: `config.ini` → `[SEARCH] HIGHLIGHT = false`

```ini
[SEARCH]
HIGHLIGHT = false  # 关闭搜索结果高亮
```

**效果**: 减少搜索时的临时内存分配

### 3. 降低 SQLite 缓存（节省 3-19 MB）

**配置**: `config.ini` → `[DB] CACHE_SIZE_KB = 1024`

```ini
[DB]
CACHE_SIZE_KB = 1024  # 从默认 20 MB 降至 1 MB
```

**效果**: 
- 默认 20 MB → 1 MB: 节省 19 MB
- 可按需调整（512/1024/2048/4096）

### 4. 调整统计更新频率（降低峰值）✅ 已默认

统计任务已优化为每 2 小时执行：

```python
# 已在 main.py 中设置
job_queue.run_repeating(update_post_stats, interval=7200, first=60)
```

### 5. 禁用搜索功能（节省 ~30-100 MB）

如果不需要搜索功能：

```ini
[SEARCH]
ENABLED = false
```

**节省内存**: ~30-100 MB（根据帖子数量）

### 6. 定期清理日志文件

```bash
# 手动清理
rm -rf logs/*.log

# 或使用 logrotate 自动清理
```

### 7. 优化搜索索引

```bash
# 运行索引优化
python3 utils/index_manager.py optimize
```

---

## 🐳 Docker 部署配置

### 默认配置（适用于大多数场景）

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G          # 内存上限
    reservations:
      cpus: '0.5'
      memory: 256M        # 预留内存
```

### 小型频道（<1000 帖子）

```yaml
deploy:
  resources:
    limits:
      memory: 256M
    reservations:
      memory: 128M
```

### 中型频道（1000-10000 帖子）

```yaml
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

### 大型频道（10000-50000 帖子）

```yaml
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 512M
```

### 超大频道（>50000 帖子）

```yaml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

---

## 📊 实际测试数据

### 测试环境
- **操作系统**: Linux (Ubuntu 22.04)
- **Python 版本**: 3.11
- **Docker**: 24.0.7

### 测试结果

| 帖子数 | 数据库大小 | 索引大小 | 内存占用 | 启动时间 |
|-------|-----------|---------|---------|---------|
| 100   | 60 KB     | 500 KB  | 155 MB  | 3 秒    |
| 1000  | 1.2 MB    | 5 MB    | 168 MB  | 4 秒    |
| 5000  | 8 MB      | 30 MB   | 195 MB  | 6 秒    |
| 10000 | 18 MB     | 70 MB   | 230 MB  | 8 秒    |
| 50000 | 120 MB    | 400 MB  | 450 MB  | 15 秒   |

---

## 🛠️ 内存查看与分析

无需额外脚本，可通过以下方式查看内存占用：

```bash
# Docker 环境
docker stats telesubmit-v2

# Linux/macOS 系统
top -o mem      # 或安装 htop

# Python 进程内查看（示例）
python3 - <<'PY'
import psutil
process = psutil.Process()
print(f"内存: {process.memory_info().rss / 1024 / 1024:.2f} MB")
PY
```

---

## 🎓 常见问题

### Q1: 为什么实际内存占用比估算高？

**可能原因**:
1. **Python 内存分配策略**: Python 不会立即释放内存
2. **峰值内存**: 统计更新时会临时占用更多内存
3. **系统缓存**: 操作系统会缓存文件数据

**建议**: 预留 50% 缓冲空间

### Q2: 如何监控实际内存占用？

**方法 1: 使用 Docker 命令**

```bash
docker stats telesubmit-v2
```

**方法 2: 使用 Bot 命令**

```
/debug  # 查看实时内存占用（仅 OWNER 可用）
```

**方法 3: 使用 psutil**

```python
import psutil
process = psutil.Process()
print(f"内存: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### Q3: 内存不足怎么办？

**短期方案**:
1. 禁用搜索功能（节省 ~30-100 MB）
2. 减少统计更新频率
3. 清理旧日志文件

**长期方案**:
1. 升级服务器内存
2. 使用独立的搜索服务（如 Elasticsearch）
3. 定期归档旧帖子

### Q4: 为什么 jieba 占用这么多内存？

**原因**: jieba 需要加载中文词典（约 20 MB）

**解决方案**:
1. 如果不需要搜索功能，禁用 `ENABLED`（位于 `[SEARCH]` 段）
2. jieba 只在搜索时使用，内存占用是一次性的

---

## 📚 相关文档

- [Docker 部署指南](DEPLOYMENT.md)
- [配置说明](config.ini.example)
- [搜索引擎说明](README.md#搜索功能)
- [索引管理器](utils/index_manager.py)

---

## 🔗 外部资源

- [Whoosh 性能优化](https://whoosh.readthedocs.io/en/latest/indexing.html#performance)
- [SQLite 内存管理](https://www.sqlite.org/memory.html)
- [Python 内存分析](https://docs.python.org/3/library/tracemalloc.html)

---



