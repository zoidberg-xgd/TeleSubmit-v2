"""
消息格式化器测试
"""
import pytest
from ui.messages import MessageFormatter


class TestMessageFormatter:
    """消息格式化器测试类"""
    
    @pytest.mark.unit
    def test_welcome_message_user(self):
        """测试普通用户欢迎消息"""
        message = MessageFormatter.welcome_message("TestUser", is_admin=False)
        
        assert "TestUser" in message
        assert "欢迎" in message
        assert "👤 用户" in message
        assert "👑 管理员" not in message
    
    @pytest.mark.unit
    def test_welcome_message_admin(self):
        """测试管理员欢迎消息"""
        message = MessageFormatter.welcome_message("AdminUser", is_admin=True)
        
        assert "AdminUser" in message
        assert "👑 管理员" in message
        assert "👤 用户" not in message
    
    @pytest.mark.unit
    def test_help_message_user(self):
        """测试普通用户帮助消息"""
        message = MessageFormatter.help_message(is_admin=False)
        
        assert "/submit" in message
        assert "/help" in message
        assert "/hot" in message
        assert "/mystats" in message
        # 不应包含管理员命令
        assert "/broadcast" not in message
        assert "/blacklist" not in message
    
    @pytest.mark.unit
    def test_help_message_admin(self):
        """测试管理员帮助消息"""
        message = MessageFormatter.help_message(is_admin=True)
        
        # 应该包含基础命令
        assert "/submit" in message
        assert "/help" in message
        # 应该包含管理员命令
        assert "/broadcast" in message
        assert "/blacklist" in message or "黑名单" in message
    
    @pytest.mark.unit
    def test_about_message(self):
        """测试关于消息"""
        message = MessageFormatter.about_message()
        
        assert "v2.0" in message
        assert "python-telegram-bot" in message
        assert "zoidberg-xgd" in message
        assert "github.com/zoidberg-xgd/TeleSubmit-v2" in message
    
    @pytest.mark.unit
    def test_submission_preview_basic(self):
        """测试基本投稿预览"""
        content = "这是测试内容"
        preview = MessageFormatter.submission_preview(content)
        
        assert "投稿预览" in preview
        assert content in preview
    
    @pytest.mark.unit
    def test_submission_preview_with_tags(self):
        """测试带标签的投稿预览"""
        content = "测试内容"
        tags = ["#Python", "#编程"]
        preview = MessageFormatter.submission_preview(content, tags=tags)
        
        assert "标签" in preview
        assert "#Python" in preview
        assert "#编程" in preview
    
    @pytest.mark.unit
    def test_submission_preview_with_media(self):
        """测试带媒体的投稿预览"""
        content = "测试内容"
        preview = MessageFormatter.submission_preview(content, media_count=3)
        
        assert "媒体文件" in preview
        assert "3" in preview
    
    @pytest.mark.unit
    def test_submission_preview_long_content(self):
        """测试长内容的投稿预览"""
        content = "a" * 300  # 超过200字符
        preview = MessageFormatter.submission_preview(content)
        
        # 应该被截断
        assert len(content) > 200
        assert "..." in preview
    
    @pytest.mark.unit
    def test_hot_posts_header(self):
        """测试热门帖子标题"""
        header = MessageFormatter.hot_posts_header(limit=10, time_filter="week")
        
        assert "热门内容" in header
        assert "本周" in header
        assert "10" in header
    
    @pytest.mark.unit
    def test_hot_post_item(self):
        """测试单个热门帖子条目"""
        post = {
            'heat_score': 123.45,
            'content': '测试内容',
            'views': 1000,
            'forwards': 50,
            'created_at': '2024-01-01 10:00:00'
        }
        
        item = MessageFormatter.hot_post_item(1, post)
        
        assert "🥇" in item  # 第一名的奖牌
        assert "123." in item  # 热度分数（1位小数）
        assert "1000" in item  # 浏览量
        assert "50" in item  # 转发量
    
    @pytest.mark.unit
    def test_hot_post_item_ranks(self):
        """测试不同排名的奖牌"""
        post = {
            'heat_score': 100.0,
            'content': '测试',
            'views': 100,
            'forwards': 10,
            'created_at': '2024-01-01'
        }
        
        item1 = MessageFormatter.hot_post_item(1, post)
        item2 = MessageFormatter.hot_post_item(2, post)
        item3 = MessageFormatter.hot_post_item(3, post)
        item4 = MessageFormatter.hot_post_item(4, post)
        
        assert "🥇" in item1
        assert "🥈" in item2
        assert "🥉" in item3
        assert "#4" in item4
    
    @pytest.mark.unit
    def test_search_results_header(self):
        """测试搜索结果标题"""
        header = MessageFormatter.search_results_header("Python", 42)
        
        assert "搜索结果" in header
        assert "Python" in header
        assert "42" in header
    
    @pytest.mark.unit
    def test_search_result_item(self):
        """测试单个搜索结果"""
        post = {
            'content': '这是一条关于Python的帖子',
            'tags': '#Python #编程',
            'created_at': '2024-01-01 10:00:00'
        }
        
        item = MessageFormatter.search_result_item(post, highlight="Python")
        
        assert "Python" in item
        assert "#Python" in item
        assert "#编程" in item
    
    @pytest.mark.unit
    def test_user_stats(self):
        """测试用户统计信息"""
        stats = {
            'total_posts': 100,
            'total_views': 10000,
            'total_forwards': 500,
            'avg_heat': 75.5,
            'top_tags': [('#Python', 30), ('#编程', 25), ('#学习', 20)]
        }
        
        message = MessageFormatter.user_stats(stats)
        
        assert "100" in message  # 总投稿数
        assert "10,000" in message or "10000" in message  # 总浏览量
        assert "500" in message  # 总转发量
        assert "75.5" in message  # 平均热度
        assert "#Python" in message
        assert "30" in message
    
    @pytest.mark.unit
    def test_user_stats_empty(self):
        """测试空统计信息"""
        stats = {
            'total_posts': 0,
            'total_views': 0,
            'total_forwards': 0,
            'avg_heat': 0,
            'top_tags': []
        }
        
        message = MessageFormatter.user_stats(stats)
        
        # 不应该抛出异常
        assert isinstance(message, str)
        assert len(message) > 0
    
    @pytest.mark.unit
    def test_admin_stats(self):
        """测试管理员统计信息"""
        stats = {
            'total_users': 1000,
            'total_posts': 5000,
            'total_views': 100000,
            'total_forwards': 2000,
            'active_users_7d': 200,
            'blacklist_count': 5
        }
        
        message = MessageFormatter.admin_stats(stats)
        
        assert "1000" in message  # 总用户数
        assert "5000" in message  # 总投稿数
        assert "100,000" in message or "100000" in message  # 总浏览量
        assert "200" in message  # 7日活跃
        assert "5" in message  # 黑名单
    
    @pytest.mark.unit
    def test_error_messages(self):
        """测试错误消息"""
        assert "失败" in MessageFormatter.error_message("general")
        assert "权限" in MessageFormatter.error_message("permission")
        assert "黑名单" in MessageFormatter.error_message("blacklist")
        assert "未找到" in MessageFormatter.error_message("not_found")
    
    @pytest.mark.unit
    def test_success_message(self):
        """测试成功消息"""
        message = MessageFormatter.success_message("提交")
        
        assert "✅" in message
        assert "提交" in message
        assert "成功" in message
    
    @pytest.mark.unit
    def test_loading_message(self):
        """测试加载消息"""
        message = MessageFormatter.loading_message()
        
        assert "处理中" in message or "⏳" in message
    
    @pytest.mark.unit
    def test_submission_guide(self):
        """测试投稿指南"""
        guide = MessageFormatter.submission_guide()
        
        assert "投稿指南" in guide
        assert "图片" in guide or "文字" in guide
        assert "标签" in guide
    
    @pytest.mark.unit
    def test_pagination_info(self):
        """测试分页信息"""
        info = MessageFormatter.pagination_info(2, 10)
        
        assert "2" in info
        assert "10" in info
        assert "页" in info
    
    @pytest.mark.unit
    def test_empty_result(self):
        """测试空结果消息"""
        message = MessageFormatter.empty_result()
        
        assert "暂无" in message or "没有" in message
    
    @pytest.mark.unit
    def test_format_number(self):
        """测试数字格式化"""
        assert MessageFormatter.format_number(100) == "100"
        assert MessageFormatter.format_number(1500) == "1.5K"
        assert MessageFormatter.format_number(1500000) == "1.5M"
    
    @pytest.mark.unit
    def test_progress_bar(self):
        """测试进度条"""
        bar1 = MessageFormatter.progress_bar(0, 100)
        bar2 = MessageFormatter.progress_bar(50, 100)
        bar3 = MessageFormatter.progress_bar(100, 100)
        
        assert isinstance(bar1, str)
        assert isinstance(bar2, str)
        assert isinstance(bar3, str)
        assert len(bar1) == len(bar2) == len(bar3)
    
    @pytest.mark.unit
    def test_progress_bar_zero_total(self):
        """测试总数为0的进度条"""
        bar = MessageFormatter.progress_bar(0, 0)
        
        assert isinstance(bar, str)
        assert "▱" in bar


class TestMessageFormatterEdgeCases:
    """消息格式化器边界情况测试"""
    
    @pytest.mark.unit
    def test_unicode_in_messages(self):
        """测试消息中的 Unicode 字符"""
        message = MessageFormatter.welcome_message("用户名👋", is_admin=False)
        
        assert "用户名👋" in message
    
    @pytest.mark.unit
    def test_html_injection_prevention(self):
        """测试 HTML 注入防护"""
        malicious_name = "<script>alert('xss')</script>"
        message = MessageFormatter.welcome_message(malicious_name, is_admin=False)
        
        # 应该包含原始内容（Telegram 会处理转义）
        assert malicious_name in message
    
    @pytest.mark.unit
    def test_empty_post_data(self):
        """测试空帖子数据"""
        post = {
            'heat_score': 0,
            'content': '',
            'views': 0,
            'forwards': 0,
            'created_at': ''
        }
        
        item = MessageFormatter.hot_post_item(1, post)
        
        # 不应该抛出异常
        assert isinstance(item, str)
    
    @pytest.mark.unit
    def test_very_long_content_truncation(self):
        """测试超长内容截断"""
        long_content = "测试" * 1000
        preview = MessageFormatter.submission_preview(long_content)
        
        # 应该被截断且不会太长
        assert len(preview) < len(long_content)
        assert "..." in preview
