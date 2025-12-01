"""
热度计算器测试
"""
import pytest
from datetime import datetime, timedelta
from utils.heat_calculator import (
    calculate_multi_message_heat,
    calculate_engagement_rate,
    calculate_completion_rate,
    get_quality_metrics
)


class TestHeatCalculator:
    """热度计算器测试类"""
    
    @pytest.mark.unit
    def test_calculate_multi_message_heat_single_post(self):
        """测试单条消息的热度计算"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 25
        }
        related_stats_list = []
        publish_time = datetime.now().timestamp()
        
        result = calculate_multi_message_heat(main_stats, related_stats_list, publish_time)
        
        assert 'heat_score' in result
        assert 'effective_views' in result
        assert 'effective_forwards' in result
        assert 'effective_reactions' in result
        assert result['effective_views'] == 1000
        assert result['effective_forwards'] == 50
        assert result['effective_reactions'] == 25
        assert result['heat_score'] > 0
    
    @pytest.mark.unit
    def test_calculate_multi_message_heat_with_related(self):
        """测试多条消息的热度计算"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 25
        }
        related_stats_list = [
            {'views': 800, 'forwards': 10, 'reactions': 15},
            {'views': 600, 'forwards': 5, 'reactions': 10}
        ]
        publish_time = datetime.now().timestamp()
        
        result = calculate_multi_message_heat(main_stats, related_stats_list, publish_time)
        
        # 验证有效浏览量的计算（主帖70% + 关联帖30%）
        expected_views = 1000 * 0.7 + (800 + 600) / 2 * 2 * 0.3
        assert result['effective_views'] == pytest.approx(expected_views, rel=0.01)
        
        # 转发量应该是最大值
        assert result['effective_forwards'] == 50
        
        # 反应数应该是加权平均
        expected_reactions = 25 * 0.5 + (15 + 10) * 0.5
        assert result['effective_reactions'] == pytest.approx(expected_reactions, rel=0.01)
    
    @pytest.mark.unit
    def test_time_decay(self):
        """测试时间衰减"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 25
        }
        related_stats_list = []
        
        # 新发布的帖子
        recent_time = datetime.now().timestamp()
        recent_result = calculate_multi_message_heat(main_stats, related_stats_list, recent_time)
        
        # 7天前的帖子（半衰期）
        old_time = (datetime.now() - timedelta(days=7)).timestamp()
        old_result = calculate_multi_message_heat(main_stats, related_stats_list, old_time)
        
        # 旧帖子的热度应该更低
        assert old_result['heat_score'] < recent_result['heat_score']
        
        # 应该约为一半（7天半衰期）
        assert old_result['heat_score'] / recent_result['heat_score'] == pytest.approx(0.5, rel=0.1)
    
    @pytest.mark.unit
    def test_calculate_engagement_rate(self):
        """测试互动率计算"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 50
        }
        related_stats_list = []
        
        rate = calculate_engagement_rate(main_stats, related_stats_list)
        
        # 互动率 = (50 + 50) / 1000 = 0.1
        assert rate == pytest.approx(0.1, rel=0.01)
    
    @pytest.mark.unit
    def test_calculate_engagement_rate_with_zero_views(self):
        """测试零浏览量的互动率计算"""
        main_stats = {
            'views': 0,
            'forwards': 0,
            'reactions': 0
        }
        related_stats_list = []
        
        rate = calculate_engagement_rate(main_stats, related_stats_list)
        
        assert rate == 0.0
    
    @pytest.mark.unit
    def test_calculate_completion_rate_single_post(self):
        """测试单帖子的完成率"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 25
        }
        related_stats_list = []
        
        rate = calculate_completion_rate(main_stats, related_stats_list)
        
        # 单帖子默认100%完成率
        assert rate == 1.0
    
    @pytest.mark.unit
    def test_calculate_completion_rate_multi_posts(self):
        """测试多帖子的完成率"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 25
        }
        related_stats_list = [
            {'views': 800, 'forwards': 10, 'reactions': 15},
            {'views': 500, 'forwards': 5, 'reactions': 10}  # 最后一条
        ]
        
        rate = calculate_completion_rate(main_stats, related_stats_list)
        
        # 完成率 = 500 / 1000 = 0.5
        assert rate == pytest.approx(0.5, rel=0.01)
    
    @pytest.mark.unit
    def test_get_quality_metrics(self):
        """测试质量指标综合计算"""
        main_stats = {
            'views': 1000,
            'forwards': 50,
            'reactions': 50
        }
        related_stats_list = [
            {'views': 800, 'forwards': 10, 'reactions': 15},
            {'views': 600, 'forwards': 5, 'reactions': 10}
        ]
        
        metrics = get_quality_metrics(main_stats, related_stats_list)
        
        assert 'engagement_rate' in metrics
        assert 'completion_rate' in metrics
        assert 'quality_score' in metrics
        assert 0 <= metrics['engagement_rate'] <= 1
        assert 0 <= metrics['completion_rate'] <= 1
        assert 0 <= metrics['quality_score'] <= 100
    
    @pytest.mark.unit
    def test_edge_case_all_zeros(self):
        """测试全零的边界情况"""
        main_stats = {
            'views': 0,
            'forwards': 0,
            'reactions': 0
        }
        related_stats_list = []
        publish_time = datetime.now().timestamp()
        
        result = calculate_multi_message_heat(main_stats, related_stats_list, publish_time)
        
        assert result['heat_score'] == 0
        assert result['effective_views'] == 0
        assert result['effective_forwards'] == 0
        assert result['effective_reactions'] == 0
