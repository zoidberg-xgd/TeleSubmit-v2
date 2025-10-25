# TeleSubmit-v2 文档导航

**更新日期**: 2025-10-25

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

目前无单独的优化总结文档，请参考根目录的 [CHANGELOG.md](../CHANGELOG.md) 获取近期优化与变更。

### Bug 修复记录

所有修复记录位于 `docs/fixes/` 目录：

| 文档 | 修复内容 |
|------|---------|
| [README](fixes/README.md) | 修复说明索引 |
| [CANCEL_COMMAND_ANALYSIS.md](fixes/CANCEL_COMMAND_ANALYSIS.md) | /cancel 命令防卡死分析 |

---

## 📁 归档文档

历史文档位于 `docs/archive/` 目录：

| 文档 | 描述 |
|------|------|
| [MULTI_MESSAGE_STATS.md](archive/MULTI_MESSAGE_STATS.md) | 多消息统计（技术背景） |
| [TAG_CLOUD_FIX_README.md](archive/TAG_CLOUD_FIX_README.md) | 标签云修复（技术细节） |
| [TESTING_GUIDE.md](archive/TESTING_GUIDE.md) | 测试清单（保留） |

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
    ├── （暂无优化总结文档）
    │
    ├── fixes/                   # Bug 修复记录
    │   ├── README.md
    │   └── CANCEL_COMMAND_ANALYSIS.md
    │
    └── archive/                 # 历史文档
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
→ [CHANGELOG.md](../CHANGELOG.md)

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
**最后更新**: 2025-10-25

