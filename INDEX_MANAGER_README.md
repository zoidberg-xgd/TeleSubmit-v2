# 索引管理器 (Index Manager)

搜索索引管理工具，提供索引重建、增量同步、优化等功能。

## 功能特性

### 1. 索引重建 (Rebuild Index)
完全重建搜索索引，支持清空现有索引后重新创建。

**使用场景:**
- 首次初始化搜索功能
- 修改了 Schema 后需要更新索引
- 索引损坏或不一致时修复

**示例:**
```python
from utils.index_manager import get_index_manager

manager = get_index_manager()
result = await manager.rebuild_index(clear_first=True)

if result['success']:
    print(f"添加了 {result['added']} 个帖子")
```

### 2. 增量同步 (Sync Index)
将数据库中的新帖子同步到搜索索引，删除不存在的帖子。

**使用场景:**
- 定期同步数据库和索引
- 添加新帖子后更新索引
- 删除帖子后清理索引

**示例:**
```python
result = await manager.sync_index()
print(f"添加: {result['added']}, 删除: {result['removed']}")
```

### 3. 索引优化 (Optimize Index)
合并索引段文件，提高搜索性能。

**使用场景:**
- 大量更新后优化索引结构
- 定期维护提升搜索速度
- 减少磁盘空间占用

**示例:**
```python
result = await manager.optimize_index()
print(result['message'])
```

### 4. 索引统计 (Index Stats)
获取数据库和索引的统计信息。

**示例:**
```python
stats = await manager.get_index_stats()
print(f"数据库: {stats['db_post_count']} 帖子")
print(f"索引: {stats['index_doc_count']} 文档")
print(f"需同步: {stats['needs_sync']}")
```

## 自动重建机制

系统启动时会自动检查索引状态：

1. **Schema 不匹配**: 自动重建索引
2. **索引缺失**: 自动创建索引
3. **数据不一致**: 尝试增量同步

**在 `main.py` 中使用:**
```python
from utils.index_manager import auto_rebuild_index_if_needed

# 在 bot 启动时调用
async def on_startup():
    result = await auto_rebuild_index_if_needed()
    if result.get('action') == 'rebuilt':
        logger.info("索引已自动重建")
```

## 使用建议

建议在集成场景中通过 `utils/index_manager.py` 的 API 进行调用与校验。
常见操作：重建（可清空）、增量同步、优化、状态统计。

## API 参考

### `IndexManager.rebuild_index(clear_first=False)`
重建搜索索引

**参数:**
- `clear_first` (bool): 是否先清空现有索引

**返回:**
```python
{
    'success': bool,
    'added': int,      # 添加的文档数
    'failed': int,     # 失败的文档数
    'time_taken': float,  # 耗时（秒）
    'errors': List[str]   # 错误信息
}
```

### `IndexManager.sync_index()`
增量同步索引

**返回:**
```python
{
    'success': bool,
    'added': int,      # 新增的文档数
    'removed': int,    # 删除的文档数
    'errors': List[str]
}
```

### `IndexManager.optimize_index()`
优化索引

**返回:**
```python
{
    'success': bool,
    'message': str     # 结果消息
}
```

### `IndexManager.get_index_stats()`
获取统计信息

**返回:**
```python
{
    'db_post_count': int,        # 数据库帖子数
    'index_doc_count': int,      # 索引文档数
    'needs_sync': bool,          # 是否需要同步
    'missing_in_index': List[str],  # 缺失的索引
    'missing_in_db': List[str]      # 多余的索引
}
```

## 注意事项

1. **并发安全**: 索引操作使用写锁，确保并发安全
2. **性能优化**: 大量更新后建议执行 `optimize_index()`
3. **错误处理**: Schema 错误会自动触发重建
4. **定期维护**: 建议定期运行 `sync_index()` 保持一致性

## 故障排除

### 索引损坏
```python
# 完全重建索引
await manager.rebuild_index(clear_first=True)
```

### Schema 不匹配
```python
# 系统会自动检测并重建
# 或手动重建:
await manager.rebuild_index(clear_first=True)
```

### 数据不一致
```python
# 增量同步修复
await manager.sync_index()
```

## 相关文件

- `utils/index_manager.py` - 索引管理器实现
- `utils/search_engine.py` - 搜索引擎核心
- `config/settings.py` - 配置文件

## 更新日志

**2025-10-25**
- ✅ 创建索引管理器
- ✅ 实现重建、同步、优化功能
- ✅ 修复数据库列名问题 (message_id)
- ✅ 添加自动重建机制
- ✅ 完善错误处理和日志

