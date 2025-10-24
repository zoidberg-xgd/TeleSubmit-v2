# 文件名搜索功能升级指南

## 功能说明

现在搜索功能已升级，支持**文件名搜索**！

### 搜索范围
- ✅ 标题
- ✅ 简介/描述
- ✅ 标签
- ✅ **文件名** ⭐ 新增

### 使用示例

```bash
# 搜索包含 "Python" 的帖子（标题、简介、标签、文件名）
/search Python

# 搜索文件名包含 "教程" 的帖子
/search 教程.pdf

# 搜索文件名包含 "小说" 的帖子
/search 小说.txt

# 结合时间过滤搜索本周的文档
/search 文档 -t week
```

## 升级步骤

### 1. 运行数据库迁移

为数据库添加 `filename` 字段：

```bash
python migrate_add_filename.py
```

### 2. 重建搜索索引

清空并重建搜索索引以包含新字段：

```bash
python migrate_to_search.py --clear
```

### 3. 查看迁移说明（可选）

```bash
python migrate_extract_filenames.py
```

此脚本会显示关于文件名提取的说明信息。

### 4. 重启机器人

```bash
./restart.sh
```

## 重要说明

### 关于历史数据

⚠️ **由于 Telegram Bot API 限制，无法自动提取历史消息的文件名。**

- ✅ **新投稿**：从现在开始，所有新发布的投稿都会自动记录文件名
- ⚠️ **历史投稿**：旧投稿的文件名字段为空，但仍可通过标题、简介、标签搜索

### 搜索建议

1. **新用户**：无需特殊操作，直接使用即可
2. **现有用户**：
   - 历史投稿可通过标题/简介/标签搜索
   - 建议在投稿时在标题或简介中包含关键文件名信息
   - 新投稿会自动支持文件名搜索

## 技术细节

### 数据库变更

- 表：`published_posts`
- 新增字段：`filename TEXT`
- 索引：自动包含在全文搜索中

### 搜索引擎变更

- Whoosh Schema 更新
- 新增 `filename` 字段（TEXT，支持中文分词）
- 多字段搜索：`['title', 'description', 'tags', 'filename']`

### 文件格式变更

- 旧格式：`document:file_id`
- 新格式：`document:file_id:filename`
- 完全向后兼容

## 验证功能

升级完成后，可以测试以下功能：

```bash
# 1. 上传一个文档文件（例如：测试文件.txt）
/start
# ... 按提示操作 ...

# 2. 发布后搜索文件名
/search 测试文件

# 3. 搜索文件扩展名
/search .txt

# 4. 结合其他搜索
/search 测试 -t week
```

## 故障排查

### 问题1：搜索不到新上传的文件名

**解决方案**：
1. 确认已运行数据库迁移
2. 确认已重建搜索索引
3. 重启机器人

### 问题2：索引报错

**解决方案**：
```bash
# 完全重建索引
rm -rf search_index/
python migrate_to_search.py --clear
```

### 问题3：数据库字段不存在

**解决方案**：
```bash
# 确保运行了数据库迁移
python migrate_add_filename.py
```

## 回滚方案

如果需要回滚到旧版本：

```bash
# 1. 回退代码
git checkout <previous_commit>

# 2. 重建索引（不包含 filename 字段）
python migrate_to_search.py --clear

# 3. 重启机器人
./restart.sh
```

注意：数据库中的 `filename` 字段会保留但不会被使用。

## 支持

如有问题，请查看日志文件或联系管理员。

