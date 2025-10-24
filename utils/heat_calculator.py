"""
多组媒体热度计算算法

解决直接累加带来的重复计数问题
"""
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


def calculate_multi_message_heat(
    main_stats: Dict[str, int],
    related_stats_list: List[Dict[str, int]],
    publish_time: float
) -> Dict[str, float]:
    """
    计算多组媒体的综合热度
    
    算法设计思路：
    1. 浏览量：主帖权重70%，其他帖子去重后累加30%
    2. 转发量：用最大值（因为转发通常只转主帖）
    3. 反应数：加权累加（主帖50%，其他帖平均分50%）
    4. 时间衰减：统一应用
    
    Args:
        main_stats: 主消息统计 {'views': int, 'forwards': int, 'reactions': int}
        related_stats_list: 关联消息统计列表
        publish_time: 发布时间戳
        
    Returns:
        {
            'effective_views': 有效浏览量,
            'effective_forwards': 有效转发量,
            'effective_reactions': 有效反应数,
            'heat_score': 最终热度分数,
            'calculation_detail': 计算详情（调试用）
        }
    """
    
    # === 1. 浏览量计算 ===
    # 假设：用户看了主帖后，有40%概率会点开回复帖
    # 公式：主帖浏览 * 70% + 其他帖平均浏览 * 30%
    main_views = main_stats['views']
    
    if related_stats_list:
        avg_related_views = sum(s['views'] for s in related_stats_list) / len(related_stats_list)
        effective_views = main_views * 0.7 + avg_related_views * len(related_stats_list) * 0.3
    else:
        effective_views = main_views
    
    # === 2. 转发量计算 ===
    # 假设：用户只会转发主帖，不会转发回复帖
    # 公式：取所有消息中的最大转发数
    all_forwards = [main_stats['forwards']] + [s['forwards'] for s in related_stats_list]
    effective_forwards = max(all_forwards) if all_forwards else 0
    
    # === 3. 反应数计算 ===
    # 假设：每条帖子的反应都是独立的
    # 公式：主帖 50% + 其他帖子平均 50%
    main_reactions = main_stats['reactions']
    
    if related_stats_list:
        total_related_reactions = sum(s['reactions'] for s in related_stats_list)
        effective_reactions = main_reactions * 0.5 + total_related_reactions * 0.5
    else:
        effective_reactions = main_reactions
    
    # === 4. 基础分数计算 ===
    # 浏览：0.3  转发：0.4（权重最高）  反应：0.3
    base_score = (
        effective_views * 0.3 +
        effective_forwards * 10 * 0.4 +  # 转发权重10倍
        effective_reactions * 5 * 0.3    # 反应权重5倍
    )
    
    # === 5. 时间衰减 ===
    # 7天半衰期
    age_days = (datetime.now().timestamp() - publish_time) / 86400
    time_decay = 2 ** (-age_days / 7)
    
    heat_score = base_score * time_decay
    
    # === 6. 返回详细结果 ===
    calculation_detail = {
        'main_views': main_views,
        'related_count': len(related_stats_list),
        'avg_related_views': sum(s['views'] for s in related_stats_list) / len(related_stats_list) if related_stats_list else 0,
        'effective_views': round(effective_views, 2),
        'effective_forwards': effective_forwards,
        'effective_reactions': round(effective_reactions, 2),
        'base_score': round(base_score, 2),
        'time_decay': round(time_decay, 4),
        'age_days': round(age_days, 2)
    }
    
    logger.debug(f"热度计算详情: {calculation_detail}")
    
    return {
        'effective_views': effective_views,
        'effective_forwards': effective_forwards,
        'effective_reactions': effective_reactions,
        'heat_score': heat_score,
        'calculation_detail': calculation_detail
    }


def calculate_engagement_rate(
    main_stats: Dict[str, int],
    related_stats_list: List[Dict[str, int]]
) -> float:
    """
    计算互动率（深度指标）
    
    互动率 = (转发 + 反应) / 浏览量
    高互动率说明内容质量好
    
    Returns:
        互动率（0-1之间的浮点数）
    """
    total_views = main_stats['views'] + sum(s['views'] for s in related_stats_list)
    total_forwards = main_stats['forwards'] + sum(s['forwards'] for s in related_stats_list)
    total_reactions = main_stats['reactions'] + sum(s['reactions'] for s in related_stats_list)
    
    if total_views == 0:
        return 0.0
    
    engagement = (total_forwards + total_reactions) / total_views
    return min(engagement, 1.0)  # 最大1.0


def calculate_completion_rate(
    main_stats: Dict[str, int],
    related_stats_list: List[Dict[str, int]]
) -> float:
    """
    计算完成率（多组媒体特有指标）
    
    完成率 = 最后一组浏览量 / 第一组浏览量
    高完成率说明内容吸引力强，用户愿意看完所有帖子
    
    Returns:
        完成率（0-1之间的浮点数）
    """
    if not related_stats_list:
        return 1.0  # 单帖子默认100%
    
    first_views = main_stats['views']
    last_views = related_stats_list[-1]['views']
    
    if first_views == 0:
        return 0.0
    
    completion = last_views / first_views
    return min(completion, 1.0)  # 理论上不会超过1，但保险起见


def get_quality_metrics(
    main_stats: Dict[str, int],
    related_stats_list: List[Dict[str, int]]
) -> Dict[str, float]:
    """
    获取内容质量指标
    
    Returns:
        {
            'engagement_rate': 互动率,
            'completion_rate': 完成率,
            'quality_score': 综合质量分（0-100）
        }
    """
    engagement = calculate_engagement_rate(main_stats, related_stats_list)
    completion = calculate_completion_rate(main_stats, related_stats_list)
    
    # 综合质量分：互动率60%，完成率40%
    quality_score = (engagement * 60 + completion * 40)
    
    return {
        'engagement_rate': round(engagement, 4),
        'completion_rate': round(completion, 4),
        'quality_score': round(quality_score, 2)
    }

