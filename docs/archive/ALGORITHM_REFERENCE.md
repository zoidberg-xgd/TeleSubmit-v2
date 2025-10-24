# 智能热度算法 - 快速参考

## 核心公式

### 1️⃣ 有效浏览量
```
有效浏览 = 主帖浏览 × 0.7 + 回复平均浏览 × 0.3 × 回复数量
```
**理由**: 避免重复计数，主帖权重更高

### 2️⃣ 有效转发量
```
有效转发 = max(主帖转发, 回复1转发, 回复2转发, ...)
```
**理由**: 用户通常只转发主帖

### 3️⃣ 有效反应数
```
有效反应 = 主帖反应 × 0.5 + 所有回复反应总和 × 0.5
```
**理由**: 每条帖子的反应都是独立的，加权平衡

### 4️⃣ 热度分数
```
基础分 = 有效浏览 × 0.3 + 有效转发 × 10 × 0.4 + 有效反应 × 5 × 0.3
时间衰减 = 2^(-天数/7)
热度分 = 基础分 × 时间衰减
```

## 质量指标

### 互动率
```
互动率 = (总转发 + 总反应) / 总浏览
```
- **高互动率** (>10%): 内容质量好，用户愿意互动
- **低互动率** (<5%): 内容可能不够吸引人

### 完成率
```
完成率 = 最后一组浏览量 / 第一组浏览量
```
- **高完成率** (>60%): 内容吸引力强，用户看完所有帖子
- **低完成率** (<30%): 用户可能对后续内容不感兴趣

### 质量分数
```
质量分 = 互动率 × 60 + 完成率 × 40
```
- 综合评估内容质量 (0-100分)

## 实际案例对比

| 指标 | 直接累加 | 智能算法 | 说明 |
|------|---------|---------|------|
| 浏览量 | 360 | 148 | 避免重复计数 |
| 转发量 | 13 | 5 | 只转发主帖 |
| 反应数 | 36 | 18 | 加权平衡 |
| **热度分** | **214** | **91** | 更接近真实热度 |
| 互动率 | - | 13.6% | 内容质量好 |
| 完成率 | - | 50% | 用户看完一半 |

**结论**: 智能算法避免了 134% 的虚高

## 参数调优位置

文件: `utils/heat_calculator.py`

```python
# 1. 浏览量权重
effective_views = main_views * 0.7 + avg_related_views * 0.3
# 可调整 0.7/0.3 比例

# 2. 反应权重
effective_reactions = main_reactions * 0.5 + total_related_reactions * 0.5
# 可调整 0.5/0.5 比例

# 3. 热度分数权重
base_score = views * 0.3 + forwards * 10 * 0.4 + reactions * 5 * 0.3
# 可调整 0.3/0.4/0.3 比例和倍数

# 4. 时间衰减
time_decay = 2 ** (-age_days / 7)
# 可调整半衰期天数
```

## 日志示例

```
INFO: 帖子 803 有 4 个关联消息，使用智能算法计算热度
INFO: 帖子 803 热度计算完成 | 
      有效浏览: 148 | 有效转发: 5 | 有效反应: 18 | 
      热度: 91.4 | 互动率: 13.6% | 完成率: 50%
```

## API

### 计算多消息热度
```python
from utils.heat_calculator import calculate_multi_message_heat

result = calculate_multi_message_heat(
    main_stats={'views': 100, 'forwards': 5, 'reactions': 10},
    related_stats_list=[
        {'views': 80, 'forwards': 3, 'reactions': 8},
        # ... 更多关联消息
    ],
    publish_time=1234567890.0
)

# result['effective_views']
# result['effective_forwards']
# result['effective_reactions']
# result['heat_score']
# result['calculation_detail']
```

### 获取质量指标
```python
from utils.heat_calculator import get_quality_metrics

metrics = get_quality_metrics(main_stats, related_stats_list)

# metrics['engagement_rate']    # 互动率
# metrics['completion_rate']    # 完成率
# metrics['quality_score']      # 质量分
```

