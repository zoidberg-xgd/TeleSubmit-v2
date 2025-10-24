# TeleSubmit v2.1.0 Release Notes

## 🎉 版本亮点

TeleSubmit v2.1.0 是一个功能丰富的更新版本，带来了强大的全文搜索功能、优化的热度统计显示、文件类型过滤等重要改进。

## ✨ 主要新功能

### 1. 🔍 全文搜索引擎
- **搜索引擎**: 集成 Whoosh 全文搜索，支持中文分词（jieba）
- **多字段搜索**: 搜索标题、描述、标签等
- **智能排序**: 按相关度和热度智能排序
- **时间筛选**: 支持按日/周/月筛选
- **搜索命令**: `/search <关键词> [-t 时间范围] [-n 数量]`

### 2. 📊 优化热门榜单显示
- **只显示主贴**: 自动过滤多组媒体的后续消息
- **可点击标题**: 直接跳转到频道帖子
- **简介预览**: 显示投稿简介（最多60字符）
- **智能数字**: 1.5w、2.3k 等简化显示
- **相对时间**: "3小时前"、"1天前" 等直观时间
- **更多标签**: 显示最多5个标签（之前3个）

### 3. 📁 文件类型过滤
- **灵活配置**: 支持扩展名、MIME类型、通配符
- **按频道定制**: 小说频道、游戏频道等不同需求
- **友好提示**: 拒绝不允许的文件时提示用户
- **配置示例**:
  ```ini
  # 小说频道
  ALLOWED_FILE_TYPES = .txt,.epub,.mobi,.pdf
  
  # 游戏频道
  ALLOWED_FILE_TYPES = .zip,.rar,.apk
  
  # 允许所有
  ALLOWED_FILE_TYPES = *
  ```

### 4. 🏷️ 标签云展示
- **可视化展示**: 按热度显示标签大小
- **可配置数量**: `/tags [数量]` 查看热门标签
- **多行格式化**: 美观的排版

### 5. 🛠️ 辅助工具
- **配置检查**: `python check_config.py` 验证配置
- **搜索迁移**: `python migrate_to_search.py` 导入现有数据
- **设置向导**: `python setup_wizard.py` 交互式配置
- **快速启动**: `./quickstart.sh` 一键部署

## 🔧 改进和优化

### 代码架构
- ✅ 模块化设计，更易维护
- ✅ 更好的错误处理
- ✅ 完善的日志系统
- ✅ 类型注解支持

### 性能优化
- ✅ 异步数据库操作
- ✅ 智能缓存机制
- ✅ 优化的热度计算
- ✅ 减少 API 调用

### 用户体验
- ✅ 更清晰的提示信息
- ✅ HTML 格式化消息
- ✅ 图标和 Emoji 美化
- ✅ 更好的错误提示

### Docker 部署
- ✅ 更新容器名称为 `telesubmit-v2`
- ✅ 增加 g++ 编译器（搜索功能需要）
- ✅ 优化健康检查
- ✅ 内存限制提升至 1GB
- ✅ 数据持久化配置

## 📦 新增依赖

```txt
whoosh >= 2.7.4      # 全文搜索引擎
jieba >= 0.42.1      # 中文分词
```

## 🔄 升级指南

### 从 v2.0.x 升级

1. **更新代码**:
   ```bash
   git pull origin main
   ```

2. **更新依赖**:
   ```bash
   pip install -r requirements.txt
   # 或使用 Docker
   docker-compose up -d --build
   ```

3. **更新配置** (添加新选项):
   ```ini
   [SEARCH]
   INDEX_DIR = data/search_index
   ENABLED = true
   
   [BOT]
   ALLOWED_FILE_TYPES = *  # 或自定义类型
   ```

4. **迁移搜索数据**:
   ```bash
   python migrate_to_search.py
   # Docker 环境
   docker-compose exec telesubmit-v2 python migrate_to_search.py
   ```

5. **重启服务**:
   ```bash
   # 直接运行
   pkill -f main.py && python main.py
   
   # Docker
   docker-compose restart
   ```

### 从 v1.x 升级

请参考 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) 中的详细升级说明。

## 🐛 Bug 修复

- 修复了多组媒体在热门榜单中重复显示的问题
- 修复了标签云格式化错误
- 修复了权限检查的一些问题
- 改进了文件上传的稳定性
- 修复了搜索结果为空时的显示问题

## 📝 文档更新

- ✅ 更新 README.md 添加新功能说明
- ✅ 新增 ADMIN_GUIDE.md 管理员指南
- ✅ 新增 DEPLOY_GUIDE.md 部署指南
- ✅ 更新 CHANGELOG.md 版本历史
- ✅ 完善代码注释

## 🎯 使用示例

### 搜索功能
```bash
# 基础搜索
/search Python

# 按时间范围搜索
/search 教程 -t week

# 限制结果数量
/search #编程 -n 20
```

### 热门榜单
```bash
# 查看热门
/hot

# 指定数量和时间
/hot 20 week
```

### 标签云
```bash
# 查看热门标签
/tags 50
```

## 🔗 相关链接

- **项目主页**: https://github.com/YOUR_USERNAME/TeleSubmit
- **问题反馈**: https://github.com/YOUR_USERNAME/TeleSubmit/issues
- **文档**: README.md | DEPLOY_GUIDE.md | ADMIN_GUIDE.md

## 🙏 致谢

感谢所有贡献者和用户的支持！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**🎉 开始使用 TeleSubmit v2.1.0 吧！**

Made with ❤️ by the TeleSubmit Team

</div>

