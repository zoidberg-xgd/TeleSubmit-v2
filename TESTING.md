# 测试指南

本文档介绍 TeleSubmit-v2 项目的测试体系和使用方法。

## 测试覆盖概览

### 核心模块覆盖率

| 模块 | 覆盖率 | 测试数 | 状态 |
|------|--------|--------|------|
| 热度计算器 | 86% | 9 | 通过 |
| UI消息格式化 | 90% | 30 | 通过 |
| 文件验证器 | 100% | 15 | 通过 |
| 工具函数 | 98% | 10+ | 通过 |

**总计**: 54+ 个测试用例，核心模块平均覆盖率 **93.5%**

---

## 测试框架

项目使用 **pytest** 作为测试框架，提供完整的单元测试、集成测试和性能测试。

## 安装测试依赖

```bash
pip install -r requirements.txt
```

测试相关依赖包括：
- `pytest` - 测试框架
- `pytest-asyncio` - 异步测试支持
- `pytest-cov` - 代码覆盖率
- `pytest-mock` - Mock 支持
- `coverage` - 覆盖率报告

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_heat_calculator.py
```

### 运行特定测试类

```bash
pytest tests/test_heat_calculator.py::TestHeatCalculator
```

### 运行特定测试方法

```bash
pytest tests/test_heat_calculator.py::TestHeatCalculator::test_calculate_multi_message_heat_single_post
```

### 按标记运行测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 排除慢速测试
pytest -m "not slow"

# 只运行数据库测试
pytest -m database
```

## 测试标记说明

项目使用以下测试标记：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试（通常 > 1秒）
- `@pytest.mark.database` - 需要数据库的测试
- `@pytest.mark.network` - 需要网络的测试
- `@pytest.mark.asyncio` - 异步测试

## 代码覆盖率

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

### 查看终端覆盖率

```bash
pytest --cov=. --cov-report=term-missing
```

## 测试目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和共享 fixtures
├── test_heat_calculator.py  # 热度计算测试
├── test_helper_functions.py # 辅助函数测试
├── test_file_validator.py   # 文件验证器测试
├── test_messages.py         # 消息格式化测试
├── test_database.py         # 数据库测试
├── test_handlers.py         # 处理器测试
└── test_integration.py      # 集成测试
```

## 测试覆盖范围

### 单元测试

- **热度计算器** (`test_heat_calculator.py`)
  - 单消息热度计算
  - 多消息热度计算
  - 时间衰减
  - 互动率计算
  - 完成率计算
  - 质量指标

- **辅助函数** (`test_helper_functions.py`)
  - 标签处理
  - Markdown 转义
  - 标题构建

- **文件验证器** (`test_file_validator.py`)
  - 图片类型验证
  - 视频类型验证
  - 文档类型验证
  - 文件大小限制

- **消息格式化** (`test_messages.py`)
  - 欢迎消息
  - 帮助消息
  - 关于消息
  - 统计消息
  - 搜索结果格式化
  - 热门帖子格式化

### 数据库测试

- **数据库初始化** (`test_database.py`)
  - 数据库创建
  - 表结构验证

- **数据库操作**
  - 插入、查询、更新、删除
  - Unicode 内容
  - 特殊字符处理
  - 并发操作

### Handlers 测试

- **命令处理器** (`test_handlers.py`)
  - /start 命令
  - /help 命令
  - /about 命令

- **搜索处理器**
  - 基本搜索
  - 无关键词处理

- **统计处理器**
  - 用户统计
  - 热门内容

- **回调处理器**
  - 按钮回调

- **错误处理器**
  - 通用错误处理
  - 网络错误处理

### 集成测试

- **端到端流程** (`test_integration.py`)
  - 完整投稿流程
  - 搜索索引和查询
  - 帖子生命周期
  - 热度排名
  - 消息格式化

- **性能测试**
  - 大数据集搜索
  - 并发数据库操作

## 编写测试

### 测试命名规范

- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试方法：`test_<function_name>_<scenario>`

### 使用 Fixtures

```python
def test_something(mock_telegram_update, mock_telegram_context):
    """使用共享 fixtures"""
    # 测试代码
    pass
```

### 异步测试

```python
@pytest.mark.asyncio
async def test_async_function():
    """异步测试"""
    result = await some_async_function()
    assert result == expected
```

### Mock 使用

```python
from unittest.mock import MagicMock, AsyncMock, patch

@patch('module.function_name')
def test_with_mock(mock_function):
    """使用 mock"""
    mock_function.return_value = 'test_value'
    # 测试代码
```

## 持续集成

测试可以集成到 CI/CD 流程中：

```yaml
# GitHub Actions 示例
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## 测试最佳实践

1. **保持测试独立** - 每个测试应该能独立运行
2. **使用有意义的断言** - 确保测试失败时能提供有用信息
3. **测试边界情况** - 包括空值、极端值、错误输入等
4. **使用参数化测试** - 对于类似的测试场景
5. **保持测试简单** - 一个测试只测试一个功能点
6. **定期运行测试** - 在提交代码前运行测试
7. **维护测试代码** - 测试代码也需要重构和维护

## 调试测试

### 显示打印输出

```bash
pytest -s
```

### 详细输出

```bash
pytest -v
```

### 显示局部变量

```bash
pytest -l
```

### 进入调试器

```bash
pytest --pdb
```

### 在第一个失败时停止

```bash
pytest -x
```

### 运行上次失败的测试

```bash
pytest --lf
```

## 性能测试

### 运行性能测试

```bash
pytest -m slow
```

### 测试执行时间

```bash
pytest --durations=10
```

## 测试报告

### 生成 JUnit XML 报告

```bash
pytest --junitxml=report.xml
```

### 生成 HTML 报告

```bash
pytest --html=report.html --self-contained-html
```

## 常见问题

### Q: 测试运行很慢怎么办？

A: 使用 `-n` 参数并行运行测试（需要安装 pytest-xdist）：
```bash
pip install pytest-xdist
pytest -n auto
```

### Q: 如何跳过某些测试？

A: 使用 `@pytest.mark.skip` 或 `-k` 参数：
```bash
pytest -k "not slow"
```

### Q: 如何测试异步代码？

A: 使用 `@pytest.mark.asyncio` 装饰器和 `async/await`

### Q: 测试覆盖率太低怎么办？

A: 运行 `pytest --cov-report=term-missing` 查看未覆盖的代码行

## 贡献测试

在提交 PR 时，请确保：

1. 所有测试通过
2. 新功能有对应的测试
3. 代码覆盖率不降低
4. 测试代码遵循项目规范

## 相关资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)

---

如有问题，请联系项目维护者或提交 Issue。
