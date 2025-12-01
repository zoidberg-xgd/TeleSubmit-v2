# 测试套件

TeleSubmit-v2 的完整测试套件。

## 快速开始

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 测试文件说明

### 单元测试

- **test_heat_calculator.py** - 热度计算算法测试
  - 单消息和多消息热度计算
  - 时间衰减测试
  - 互动率和完成率测试
  - 边界情况测试

- **test_helper_functions.py** - 辅助工具函数测试
  - 标签处理和格式化
  - Markdown 转义
  - Caption 构建
  - Unicode 和特殊字符处理

- **test_file_validator.py** - 文件验证器测试
  - 图片/视频/文档类型验证
  - 文件大小限制测试
  - 文件名处理测试

- **test_messages.py** - UI 消息格式化测试
  - 所有消息模板测试
  - 格式化函数测试
  - 边界情况和注入防护测试

### 数据库测试

- **test_database.py** - 数据库操作测试
  - 数据库初始化
  - CRUD 操作
  - Unicode 和特殊字符
  - 并发操作测试

### Handler 测试

- **test_handlers.py** - 命令和回调处理器测试
  - 命令处理器（/start, /help, /about 等）
  - 搜索处理器
  - 统计处理器
  - 回调处理器
  - 错误处理器
  - 投稿和发布流程

### 集成测试

- **test_integration.py** - 端到端集成测试
  - 完整投稿流程
  - 搜索索引和查询
  - 数据库生命周期
  - 热度计算和排名
  - 性能测试

## 测试标记

使用 pytest 标记来分类运行测试：

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 只运行数据库测试
pytest -m database
```

可用标记：
- `@pytest.mark.unit` - 快速单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试（> 1秒）
- `@pytest.mark.database` - 需要数据库
- `@pytest.mark.network` - 需要网络连接

## Fixtures

### 共享 Fixtures (conftest.py)

- `temp_dir` - 临时测试目录
- `sample_post_data` - 示例投稿数据
- `sample_stats` - 示例统计数据
- `mock_telegram_update` - 模拟 Telegram Update
- `mock_telegram_context` - 模拟 Telegram Context
- `mock_database` - 模拟数据库
- `mock_config` - 模拟配置

## 测试覆盖率目标

项目目标测试覆盖率：

- **整体覆盖率**: > 80%
- **核心业务逻辑**: > 90%
- **工具函数**: > 95%
- **UI 格式化**: > 85%

当前覆盖率可以通过以下命令查看：

```bash
pytest --cov=. --cov-report=term-missing
```

## 编写新测试

### 测试文件命名

- 测试文件必须以 `test_` 开头
- 测试类必须以 `Test` 开头
- 测试方法必须以 `test_` 开头

### 示例测试

```python
import pytest

class TestMyFeature:
    """功能测试类"""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """测试基本功能"""
        result = my_function()
        assert result == expected_value
    
    @pytest.mark.unit
    def test_edge_case(self):
        """测试边界情况"""
        result = my_function(edge_case_input)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await my_async_function()
        assert result == expected_value
```

## 持续集成

项目配置了 GitHub Actions 自动运行测试：

- **触发条件**: push 到 main/develop 分支，或者 PR
- **测试环境**: Python 3.9, 3.10, 3.11, 3.12
- **测试内容**:
  - 单元测试
  - 集成测试
  - 代码覆盖率
  - 代码质量检查
  - 安全扫描

## 常见问题

### Q: 如何调试失败的测试？

```bash
# 使用 -v 显示详细信息
pytest -v

# 使用 -s 显示打印输出
pytest -s

# 使用 --pdb 进入调试器
pytest --pdb

# 显示局部变量
pytest -l
```

### Q: 如何运行单个测试？

```bash
pytest tests/test_heat_calculator.py::TestHeatCalculator::test_calculate_multi_message_heat_single_post
```

### Q: 如何加速测试？

```bash
# 并行运行（需要安装 pytest-xdist）
pip install pytest-xdist
pytest -n auto

# 只运行快速测试
pytest -m "not slow"
```

### Q: 测试覆盖率太低怎么办？

1. 运行 `pytest --cov=. --cov-report=term-missing`
2. 查看未覆盖的代码行
3. 为这些代码添加测试


## 相关文档

- [完整测试指南](../TESTING.md)
- [pytest 文档](https://docs.pytest.org/)
- [项目贡献指南](../CONTRIBUTING.md)
