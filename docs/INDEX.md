# TeleSubmit-v2 文档导航

**更新日期**: 2025-10-24

---

## 📚 主要文档

### 新手入门

| 文档 | 描述 | 位置 |
|------|------|------|
| [README.md](../README.md) | 项目主文档，快速开始 | 根目录 |
| [DEPLOYMENT.md](../DEPLOYMENT.md) | 部署指南（Docker/手动） | 根目录 |
| [ADMIN_GUIDE.md](../ADMIN_GUIDE.md) | 管理员使用指南 | 根目录 |

### 版本更新

| 文档 | 描述 | 位置 |
|------|------|------|
| [CHANGELOG.md](../CHANGELOG.md) | 版本更新历史 | 根目录 |

### 功能说明

| 文档 | 描述 | 位置 |
|------|------|------|
| [STATS_FAQ.md](../STATS_FAQ.md) | 统计功能常见问题 | 根目录 |

---

## 🔧 技术文档

### 优化记录

| 文档 | 描述 | 位置 |
|------|------|------|
| [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) | 代码优化总结（2024-10） | docs/ |

### Bug 修复记录

所有修复记录位于 `docs/fixes/` 目录：

| 文档 | 修复内容 | 日期 |
|------|---------|------|
| [KEYBOARD_FIX_SUMMARY.md](fixes/KEYBOARD_FIX_SUMMARY.md) | 键盘显示问题修复 | 2024-10-24 |
| [CANCEL_COMMAND_ANALYSIS.md](fixes/CANCEL_COMMAND_ANALYSIS.md) | /cancel 命令防卡死分析 | 2024-10-24 |
| [CHANGELOG_DELETE_FIX.md](fixes/CHANGELOG_DELETE_FIX.md) | 删除功能修复 | 2024-10-24 |
| [NETWORK_FIX.md](fixes/NETWORK_FIX.md) | 网络问题修复 | 2024-10-24 |
| [SEARCH_FILENAME_FIX.md](fixes/SEARCH_FILENAME_FIX.md) | 搜索文件名修复 | 2024-10-24 |

---

## 📁 归档文档

历史文档位于 `docs/archive/` 目录：

| 文档 | 描述 |
|------|------|
| [ALGORITHM_REFERENCE.md](archive/ALGORITHM_REFERENCE.md) | 热度算法参考 |
| [BUGFIX_SUMMARY.md](archive/BUGFIX_SUMMARY.md) | 早期 Bug 修复总结 |
| [COMMAND_PERMISSION_FIX.md](archive/COMMAND_PERMISSION_FIX.md) | 命令权限修复 |
| [EASY_START.md](archive/EASY_START.md) | 快速开始（旧版） |
| [MULTI_MESSAGE_STATS.md](archive/MULTI_MESSAGE_STATS.md) | 多消息统计 |
| [TAG_CLOUD_FIX_README.md](archive/TAG_CLOUD_FIX_README.md) | 标签云修复 |
| [TESTING_GUIDE.md](archive/TESTING_GUIDE.md) | 测试指南 |

---

## 🗂️ 文档结构

```
TeleSubmit-v2/
├── README.md                    # 主文档
├── CHANGELOG.md                 # 版本历史
├── DEPLOYMENT.md                # 部署指南
├── ADMIN_GUIDE.md              # 管理指南
├── STATS_FAQ.md                 # 统计FAQ
│
└── docs/
    ├── INDEX.md                 # 本文档（导航）
    ├── OPTIMIZATION_SUMMARY.md  # 优化总结
    ├── 测试新文档上传.md
    │
    ├── fixes/                   # Bug 修复记录
    │   ├── KEYBOARD_FIX_SUMMARY.md
    │   ├── CANCEL_COMMAND_ANALYSIS.md
    │   ├── CHANGELOG_DELETE_FIX.md
    │   ├── NETWORK_FIX.md
    │   └── SEARCH_FILENAME_FIX.md
    │
    └── archive/                 # 历史文档
        ├── ALGORITHM_REFERENCE.md
        ├── BUGFIX_SUMMARY.md
        ├── COMMAND_PERMISSION_FIX.md
        ├── EASY_START.md
        ├── MULTI_MESSAGE_STATS.md
        ├── TAG_CLOUD_FIX_README.md
        └── TESTING_GUIDE.md
```

---

## 🔍 快速查找

### 我想...

**部署 Bot**
→ [DEPLOYMENT.md](../DEPLOYMENT.md)

**了解管理命令**
→ [ADMIN_GUIDE.md](../ADMIN_GUIDE.md)

**查看统计功能**
→ [STATS_FAQ.md](../STATS_FAQ.md)

**了解最新更新**
→ [CHANGELOG.md](../CHANGELOG.md)

**查看 Bug 修复**
→ [docs/fixes/](fixes/)

**了解代码优化**
→ [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)

---

## 📝 文档维护

### 添加新文档

1. **Bug 修复**: 添加到 `docs/fixes/`
2. **功能文档**: 添加到根目录
3. **技术文档**: 添加到 `docs/`
4. **过时文档**: 移动到 `docs/archive/`

### 更新此文档

添加新文档后，请更新 `docs/INDEX.md` 中的相应链接。

---

**维护人员**: Bot 开发团队  
**最后更新**: 2025-10-24

