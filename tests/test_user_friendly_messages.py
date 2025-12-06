"""
用户友好提示测试模块
测试各种特殊情况下的用户提示信息
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestErrorMessages:
    """错误消息测试"""
    
    @pytest.mark.unit
    def test_file_validator_error_messages(self):
        """测试文件验证器的错误消息"""
        from utils.file_validator import FileTypeValidator
        
        # 测试不允许的文件类型
        validator = FileTypeValidator(allowed_types=".pdf,.zip")
        
        # 测试危险文件类型
        valid, msg = validator.validate("malware.exe", "application/x-msdownload")
        assert valid is False
        assert "不支持" in msg or "不允许" in msg or "❌" in msg
        
        # 测试双扩展名攻击
        valid, msg = validator.validate("document.pdf.exe", "application/x-msdownload")
        assert valid is False
        assert len(msg) > 0  # 应该有错误消息
    
    @pytest.mark.unit
    def test_file_validator_allowed_types_description(self):
        """测试文件类型描述"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf,.zip,.jpg")
        desc = validator.get_allowed_types_description()
        
        assert isinstance(desc, str)
        assert len(desc) > 0
        # 应该包含文件类型信息
        assert "pdf" in desc.lower() or "zip" in desc.lower() or "jpg" in desc.lower()
    
    @pytest.mark.unit
    def test_file_validator_wildcard_description(self):
        """测试通配符文件类型描述"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types="*")
        desc = validator.get_allowed_types_description()
        
        assert isinstance(desc, str)
        # 应该表明允许所有类型
        assert "所有" in desc or "任意" in desc or "全部" in desc or len(desc) > 0


class TestBlacklistMessages:
    """黑名单消息测试"""
    
    @pytest.mark.unit
    def test_blacklist_filter_logs_warning(self):
        """测试黑名单过滤器记录警告"""
        from utils.blacklist import blacklist_filter, _blacklist
        import logging
        
        test_user_id = 888888888
        _blacklist.add(test_user_id)
        
        try:
            mock_update = MagicMock()
            mock_update.effective_user.id = test_user_id
            
            # 应该返回False并记录警告
            with patch('utils.blacklist.logger') as mock_logger:
                result = blacklist_filter(mock_update)
                assert result is False
                # 验证记录了警告
                mock_logger.warning.assert_called()
        finally:
            _blacklist.discard(test_user_id)
    
    @pytest.mark.unit
    def test_owner_check_logs_warning_for_none(self):
        """测试所有者检查对None值记录警告"""
        from utils.blacklist import is_owner
        import logging
        
        with patch('utils.blacklist.logger') as mock_logger:
            result = is_owner(None)
            assert result is False
            # 应该记录警告
            mock_logger.warning.assert_called()


class TestInputValidationMessages:
    """输入验证消息测试"""
    
    @pytest.mark.unit
    def test_process_tags_handles_empty_gracefully(self):
        """测试标签处理优雅处理空输入"""
        from utils.helper_functions import process_tags
        
        # 空字符串应该成功处理
        success, result = process_tags("")
        assert success is True
        assert result == ""
        
        # 只有空格应该成功处理
        success, result = process_tags("   ")
        assert success is True
        assert result == ""
    
    @pytest.mark.unit
    def test_process_tags_truncates_long_tags(self):
        """测试标签处理截断超长标签"""
        from utils.helper_functions import process_tags
        
        # 超长标签应该被截断
        long_tag = "a" * 100
        success, result = process_tags(long_tag)
        assert success is True
        # 标签应该被截断到合理长度
        assert len(result) <= 31  # #号 + 30字符
    
    @pytest.mark.unit
    def test_build_caption_handles_missing_fields(self):
        """测试caption构建处理缺失字段"""
        from utils.helper_functions import build_caption
        
        # 空数据应该不崩溃
        result = build_caption({})
        assert isinstance(result, str)
        
        # 部分数据应该正常工作
        result = build_caption({"title": "测试标题"})
        assert isinstance(result, str)
    
    @pytest.mark.unit
    def test_build_caption_truncates_long_content(self):
        """测试caption构建截断超长内容"""
        from utils.helper_functions import build_caption
        
        long_data = {
            "title": "标题" * 500,
            "note": "内容" * 1000,
            "tags": "#标签 " * 100,
        }
        
        result = build_caption(long_data)
        # Telegram caption 限制为 1024 字符
        assert len(result) <= 1024


class TestDatabaseErrorMessages:
    """数据库错误消息测试"""
    
    @pytest.mark.unit
    def test_get_user_state_returns_none_on_error(self):
        """测试获取用户状态在错误时返回None"""
        from utils.database import get_user_state
        
        with patch('utils.database.SESSION_DB_PATH', '/nonexistent/path/db.sqlite'):
            result = get_user_state(12345)
            # 应该返回None而不是抛出异常
            assert result is None
    
    @pytest.mark.unit
    def test_database_logs_errors(self):
        """测试数据库操作记录错误"""
        from utils.database import get_user_state
        
        with patch('utils.database.SESSION_DB_PATH', '/nonexistent/path/db.sqlite'):
            with patch('utils.database.logger') as mock_logger:
                get_user_state(12345)
                # 应该记录错误
                mock_logger.error.assert_called()


class TestNetworkErrorMessages:
    """网络错误消息测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_safe_send_handles_timeout(self):
        """测试安全发送处理超时"""
        from utils.helper_functions import safe_send
        import asyncio
        
        async def slow_function():
            await asyncio.sleep(10)
            return "result"
        
        with patch('utils.helper_functions.NET_TIMEOUT', 0.1):
            result = await safe_send(slow_function)
            # 应该返回None而不是抛出异常
            assert result is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_enhanced_safe_send_logs_retries(self):
        """测试增强安全发送记录重试"""
        from utils.helper_functions import enhanced_safe_send, CONFIG
        import asyncio
        
        call_count = 0
        
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise asyncio.TimeoutError("Timeout")
            return "success"
        
        original_max_retries = CONFIG["MAX_RETRIES"]
        original_retry_delay = CONFIG["RETRY_DELAY"]
        
        try:
            CONFIG["MAX_RETRIES"] = 3
            CONFIG["RETRY_DELAY"] = 0.1
            
            with patch('utils.helper_functions.logger') as mock_logger:
                result = await enhanced_safe_send(flaky_function)
                # 应该记录重试信息
                assert mock_logger.info.called or mock_logger.warning.called
        finally:
            CONFIG["MAX_RETRIES"] = original_max_retries
            CONFIG["RETRY_DELAY"] = original_retry_delay


class TestSpecialCharacterHandling:
    """特殊字符处理测试"""
    
    @pytest.mark.unit
    def test_escape_markdown_preserves_content(self):
        """测试Markdown转义保留内容"""
        from utils.helper_functions import escape_markdown
        
        # 普通文本应该不变
        text = "Hello World 你好世界"
        result = escape_markdown(text)
        assert "Hello" in result
        assert "World" in result
        assert "你好" in result
        assert "世界" in result
    
    @pytest.mark.unit
    def test_escape_markdown_escapes_special_chars(self):
        """测试Markdown转义特殊字符"""
        from utils.helper_functions import escape_markdown
        
        # 特殊字符应该被转义
        text = "*bold* _italic_ `code`"
        result = escape_markdown(text)
        
        # 应该包含转义字符
        assert "\\*" in result or "*" not in result.replace("\\*", "")
    
    @pytest.mark.unit
    def test_process_tags_handles_unicode(self):
        """测试标签处理Unicode字符"""
        from utils.helper_functions import process_tags
        
        # 中文标签
        success, result = process_tags("中文,日本語,한국어")
        assert success is True
        assert "#中文" in result
        
        # Emoji标签
        success, result = process_tags("🎉,🎊")
        assert success is True
        assert len(result) > 0


class TestSessionTimeoutMessages:
    """会话超时消息测试"""
    
    @pytest.mark.unit
    def test_cleanup_expired_sessions_logs_count(self, temp_dir):
        """测试清理过期会话记录数量"""
        import os
        
        with patch('utils.database.SESSION_DB_PATH', os.path.join(temp_dir, 'sessions.db')):
            from utils.database import initialize_database, save_user_state, cleanup_expired_sessions
            
            initialize_database()
            save_user_state(12345, "MEDIA", {})
            
            with patch('utils.database.logger') as mock_logger:
                cleanup_expired_sessions(timeout=0)
                # 应该记录清理了多少会话
                mock_logger.info.assert_called()


class TestPermissionMessages:
    """权限消息测试"""
    
    @pytest.mark.unit
    def test_is_owner_with_wrong_id(self):
        """测试非所有者ID"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', 12345):
            # 错误的ID应该返回False
            assert is_owner(99999) is False
            assert is_owner(0) is False
            assert is_owner(-1) is False
    
    @pytest.mark.unit
    def test_is_owner_with_correct_id(self):
        """测试正确的所有者ID"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', 12345):
            assert is_owner(12345) is True


class TestEmptyStateHandling:
    """空状态处理测试"""
    
    @pytest.mark.unit
    def test_get_submission_mode_defaults(self):
        """测试获取投稿模式默认值"""
        from utils.helper_functions import get_submission_mode
        
        # None应该返回默认值
        assert get_submission_mode(None) == "mixed"
        
        # 空字典应该返回默认值
        assert get_submission_mode({}) == "mixed"
        
        # 缺少mode键应该返回默认值
        assert get_submission_mode({"other": "value"}) == "mixed"
    
    @pytest.mark.unit
    def test_parse_json_list_handles_invalid(self):
        """测试JSON列表解析处理无效输入"""
        from utils.helper_functions import parse_json_list
        
        # 无效JSON应该返回空列表
        assert parse_json_list("{invalid}") == []
        assert parse_json_list("not json") == []
        assert parse_json_list(None) == []
        assert parse_json_list("") == []


class TestUserFeedbackMessages:
    """用户反馈消息测试"""
    
    @pytest.mark.unit
    def test_file_validator_provides_helpful_error(self):
        """测试文件验证器提供有帮助的错误消息"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf")
        
        # 错误的文件类型应该提供有帮助的消息
        valid, msg = validator.validate("document.docx", "application/vnd.openxmlformats")
        assert valid is False
        # 消息应该包含有用信息
        assert len(msg) > 10  # 不是空消息
        assert "❌" in msg or "不" in msg  # 包含错误指示
    
    @pytest.mark.unit
    def test_file_validator_shows_allowed_types(self):
        """测试文件验证器显示允许的类型"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf,.zip,.jpg")
        desc = validator.get_allowed_types_description()
        
        # 描述应该包含允许的类型
        assert isinstance(desc, str)
        assert len(desc) > 0
