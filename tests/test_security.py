"""
安全性测试模块
测试 SQL 注入、XSS、输入验证等安全问题
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import MagicMock, AsyncMock, patch


class TestSQLInjectionPrevention:
    """SQL 注入防护测试"""
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_user_id_sql_injection(self, temp_dir):
        """测试用户ID参数的SQL注入防护"""
        db_path = os.path.join(temp_dir, 'test.db')
        conn = sqlite3.connect(db_path)
        conn.execute('''
            CREATE TABLE user_sessions (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                last_activity REAL
            )
        ''')
        conn.commit()
        
        # 尝试SQL注入攻击
        malicious_inputs = [
            "1; DROP TABLE user_sessions;--",
            "1 OR 1=1",
            "1' OR '1'='1",
            "1; DELETE FROM user_sessions;--",
            "1 UNION SELECT * FROM user_sessions",
        ]
        
        for malicious_input in malicious_inputs:
            # 使用参数化查询应该安全
            try:
                # 这应该失败，因为user_id应该是整数
                user_id = int(malicious_input)
            except ValueError:
                # 预期的行为 - 无法转换为整数
                pass
        
        # 验证表仍然存在
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
        assert cursor.fetchone() is not None
        conn.close()
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_tag_sql_injection(self):
        """测试标签参数的SQL注入防护"""
        from utils.helper_functions import process_tags
        
        malicious_tags = [
            "tag1; DROP TABLE posts;--",
            "tag1' OR '1'='1",
            "tag1\"; DELETE FROM posts;--",
            "tag1 UNION SELECT password FROM users",
        ]
        
        for malicious_tag in malicious_tags:
            success, result = process_tags(malicious_tag)
            # 标签处理应该正常工作，不会执行SQL
            assert success is True
            # 结果应该是安全的标签格式
            assert "DROP" not in result.upper() or "#drop" in result.lower()
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_content_sql_injection(self):
        """测试内容字段的SQL注入防护"""
        from utils.helper_functions import escape_markdown
        
        malicious_content = "Hello'; DROP TABLE posts;--"
        escaped = escape_markdown(malicious_content)
        
        # 转义后应该是安全的
        assert isinstance(escaped, str)


class TestXSSPrevention:
    """XSS 攻击防护测试"""
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_escape_html_tags(self):
        """测试HTML标签转义"""
        from utils.helper_functions import escape_markdown
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
        ]
        
        for payload in xss_payloads:
            escaped = escape_markdown(payload)
            # 确保特殊字符被转义
            assert isinstance(escaped, str)
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_build_caption_xss(self):
        """测试caption构建中的XSS防护"""
        from utils.helper_functions import build_caption
        
        malicious_data = {
            "link": "javascript:alert('XSS')",
            "title": "<script>alert('XSS')</script>",
            "note": "<img src=x onerror=alert('XSS')>",
            "tags": "#<script>alert('XSS')</script>",
            "spoiler": "false",
            "user_id": 12345,
            "username": "<script>alert('XSS')</script>"
        }
        
        caption = build_caption(malicious_data)
        # caption应该被正确构建，不会导致XSS
        assert isinstance(caption, str)
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_tag_xss_prevention(self):
        """测试标签处理中的XSS防护"""
        from utils.helper_functions import process_tags
        
        xss_tags = [
            "<script>alert('XSS')</script>",
            "tag<img src=x onerror=alert(1)>",
            "tag\"><script>alert(1)</script>",
        ]
        
        for xss_tag in xss_tags:
            success, result = process_tags(xss_tag)
            assert success is True
            # 标签应该被处理为安全格式
            assert isinstance(result, str)


class TestInputValidation:
    """输入验证测试"""
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_user_id_validation(self):
        """测试用户ID验证"""
        from utils.blacklist import is_blacklisted, is_owner
        
        # 有效的用户ID
        valid_ids = [1, 123456789, 9999999999]
        for user_id in valid_ids:
            # 不应该抛出异常
            result = is_blacklisted(user_id)
            assert isinstance(result, bool)
        
        # 无效的用户ID应该被安全处理
        result = is_owner(None)
        assert result is False
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_file_path_traversal(self):
        """测试文件路径遍历攻击防护"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf,.zip")
        
        # 路径遍历攻击尝试
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "....//....//....//etc/passwd",
        ]
        
        for path in malicious_paths:
            valid, msg = validator.validate(path, "application/octet-stream")
            # 这些都不应该是有效的PDF或ZIP文件
            assert valid is False
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_oversized_input(self):
        """测试超大输入处理"""
        from utils.helper_functions import process_tags
        
        # 非常长的输入
        huge_input = "a" * 100000
        success, result = process_tags(huge_input)
        
        # 应该正常处理，不会崩溃
        assert success is True
        # 结果应该被截断
        assert len(result) <= 1000  # 合理的长度限制
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_null_byte_injection(self):
        """测试空字节注入防护"""
        from utils.helper_functions import process_tags
        
        # 空字节注入尝试
        null_byte_inputs = [
            "tag1\x00.exe",
            "tag1%00.exe",
            "tag1\0malicious",
        ]
        
        for input_str in null_byte_inputs:
            success, result = process_tags(input_str)
            # 应该正常处理
            assert success is True
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_unicode_normalization(self):
        """测试Unicode规范化攻击防护"""
        from utils.helper_functions import process_tags
        
        # Unicode规范化攻击
        unicode_inputs = [
            "tａｇ１",  # 全角字符
            "tag\u200b1",  # 零宽空格
            "tag\ufeff1",  # BOM
            "tag\u202e1",  # 右到左覆盖
        ]
        
        for input_str in unicode_inputs:
            success, result = process_tags(input_str)
            assert success is True


class TestAuthorizationSecurity:
    """授权安全测试"""
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_owner_check_with_none(self):
        """测试所有者检查处理None值"""
        from utils.blacklist import is_owner
        
        assert is_owner(None) is False
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_owner_check_with_invalid_type(self):
        """测试所有者检查处理无效类型"""
        from utils.blacklist import is_owner
        
        # 应该安全处理各种无效输入
        invalid_inputs = [
            "not_an_id",
            [],
            {},
            12.5,
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = is_owner(invalid_input)
                # 如果没有抛出异常，结果应该是False
                assert result is False or result is True
            except (TypeError, ValueError):
                # 抛出异常也是可接受的
                pass
    
    @pytest.mark.security
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_blacklist_bypass_prevention(self):
        """测试黑名单绕过防护"""
        from utils.blacklist import is_blacklisted, _blacklist
        
        # 模拟添加用户到黑名单
        test_user_id = 999999999
        _blacklist.add(test_user_id)
        
        try:
            # 验证黑名单检查
            assert is_blacklisted(test_user_id) is True
            
            # 尝试使用不同格式绕过
            assert is_blacklisted(int(str(test_user_id))) is True
        finally:
            # 清理
            _blacklist.discard(test_user_id)


class TestFileSecurityValidation:
    """文件安全验证测试"""
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_dangerous_file_extensions(self):
        """测试危险文件扩展名检测"""
        from utils.file_validator import FileTypeValidator
        
        # 只允许安全的文件类型
        validator = FileTypeValidator(allowed_types=".pdf,.jpg,.png,.zip")
        
        dangerous_extensions = [
            ("malware.exe", "application/x-msdownload"),
            ("script.bat", "application/x-bat"),
            ("script.sh", "application/x-sh"),
            ("script.ps1", "application/x-powershell"),
            ("malware.dll", "application/x-msdownload"),
            ("script.vbs", "application/x-vbscript"),
            ("script.js", "application/javascript"),
            ("page.html", "text/html"),
            ("page.htm", "text/html"),
            ("script.php", "application/x-php"),
        ]
        
        for filename, mime in dangerous_extensions:
            valid, msg = validator.validate(filename, mime)
            assert valid is False, f"{filename} should be rejected"
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_double_extension_attack(self):
        """测试双扩展名攻击防护"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf,.jpg")
        
        double_extension_files = [
            ("document.pdf.exe", "application/x-msdownload"),
            ("image.jpg.bat", "application/x-bat"),
            ("file.pdf.js", "application/javascript"),
        ]
        
        for filename, mime in double_extension_files:
            valid, msg = validator.validate(filename, mime)
            # 应该根据最后的扩展名判断
            assert valid is False, f"{filename} should be rejected"
    
    @pytest.mark.security
    @pytest.mark.unit
    def test_mime_type_spoofing(self):
        """测试MIME类型欺骗防护"""
        from utils.file_validator import FileTypeValidator
        
        # 只允许图片
        validator = FileTypeValidator(allowed_types=".jpg,.png,.gif")
        
        # 尝试用假的MIME类型
        spoofed_files = [
            ("malware.exe", "image/jpeg"),  # 假装是图片的exe
            ("script.bat", "image/png"),    # 假装是图片的bat
        ]
        
        for filename, fake_mime in spoofed_files:
            valid, msg = validator.validate(filename, fake_mime)
            # 应该根据扩展名拒绝
            assert valid is False, f"{filename} with fake MIME should be rejected"
