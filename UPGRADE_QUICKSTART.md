# 文件名搜索功能 - 快速升级指南

## 一键升级

对于已有系统，只需运行以下命令即可完成升级：

```bash
# 1. 更新代码
git pull

# 2. 运行数据库迁移
python migrate_add_filename.py

# 3. 重建搜索索引
echo "y" | python migrate_to_search.py --clear

# 4. 重启机器人
./restart.sh
```

## 验证功能

升级完成后，测试文件名搜索：

```bash
# 1. 上传一个文档文件（例如：test.txt）
# 在 Telegram 中发送 /submit，按提示上传文档

# 2. 发布后搜索文件名
# 在 Telegram 中发送 /search test.txt
```

## 新功能说明

✨ 现在搜索支持**文件名**字段！

### 搜索范围

- ✅ 标题
- ✅ 简介/描述
- ✅ 标签
- ✅ **文件名** ⭐ 新增

### 使用示例

```bash
/search Python教程    # 搜索标题、简介、标签、文件名
/search 小说.txt      # 搜索包含"小说"的文件名
/search #编程         # 搜索标签
/search 文件 -t week  # 搜索本周的文件
```

## 注意事项

⚠️ **关于历史数据**：
- 新投稿会自动记录文件名
- 旧投稿的文件名字段为空（这是正常的）
- 旧投稿仍可通过标题、简介、标签搜索

## 详细升级指南

如需了解更多技术细节，请查看 [FILENAME_SEARCH_UPGRADE.md](FILENAME_SEARCH_UPGRADE.md)

## 问题排查

### 问题：搜索不到新上传的文件名

**解决方案**：
1. 确认已运行 `migrate_add_filename.py`
2. 确认已运行 `migrate_to_search.py --clear`
3. 重启机器人：`./restart.sh`

### 问题：迁移报错

**解决方案**：
```bash
# 完全重建索引
rm -rf data/search_index/
echo "y" | python migrate_to_search.py --clear
./restart.sh
```

## 回滚方案

如需回滚到旧版本：

```bash
git checkout <previous_commit>
echo "y" | python migrate_to_search.py --clear
./restart.sh
```

---

🎉 升级完成！享受新的文件名搜索功能！

