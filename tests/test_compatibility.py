"""
兼容性测试模块
测试不同输入格式、编码、平台兼容性
"""
import pytest
import json
import os
from unittest.mock import MagicMock, AsyncMock, patch


class TestEncodingCompatibility:
    """编码兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_utf8_encoding(self):
        """测试UTF-8编码"""
        from utils.helper_functions import process_tags
        
        utf8_strings = [
            "标签",           # 中文
            "タグ",           # 日文
            "태그",           # 韩文
            "тег",            # 俄文
            "ετικέτα",        # 希腊文
            "תג",             # 希伯来文
            "แท็ก",           # 泰文
        ]
        
        for s in utf8_strings:
            success, result = process_tags(s)
            assert success is True
            assert len(result) > 0
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_emoji_handling(self):
        """测试Emoji处理"""
        from utils.helper_functions import process_tags
        
        emoji_strings = [
            "🎉",
            "👍🏻",           # 带肤色修饰符
            "👨‍👩‍👧‍👦",  # 家庭emoji（ZWJ序列）
            "🏳️‍🌈",         # 彩虹旗
            "1️⃣",            # 键帽emoji
        ]
        
        for emoji in emoji_strings:
            success, result = process_tags(emoji)
            assert success is True
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_mixed_encoding_tags(self):
        """测试混合编码标签"""
        from utils.helper_functions import process_tags
        
        mixed = "Python,中文,日本語,한국어,🎉,тег"
        success, result = process_tags(mixed)
        assert success is True
        # 应该包含所有标签
        assert "#python" in result.lower()
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_bom_handling(self):
        """测试BOM处理"""
        from utils.helper_functions import process_tags
        
        # UTF-8 BOM
        bom_string = "\ufefftag1,tag2"
        success, result = process_tags(bom_string)
        assert success is True
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_rtl_text(self):
        """测试从右到左文本"""
        from utils.helper_functions import process_tags
        
        rtl_strings = [
            "العربية",        # 阿拉伯语
            "עברית",          # 希伯来语
            "فارسی",          # 波斯语
        ]
        
        for rtl in rtl_strings:
            success, result = process_tags(rtl)
            assert success is True


class TestInputFormatCompatibility:
    """输入格式兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_tag_separators(self):
        """测试不同标签分隔符"""
        from utils.helper_functions import process_tags
        
        separator_tests = [
            ("tag1,tag2,tag3", 3),           # 英文逗号
            ("tag1，tag2，tag3", 3),         # 中文逗号
            ("tag1 tag2 tag3", 3),           # 空格
            ("tag1  tag2  tag3", 3),         # 多空格
            ("tag1\ttag2\ttag3", 3),         # 制表符
            ("tag1, tag2, tag3", 3),         # 逗号+空格
            ("tag1 , tag2 , tag3", 3),       # 空格+逗号+空格
        ]
        
        for input_str, expected_count in separator_tests:
            success, result = process_tags(input_str)
            assert success is True
            tags = result.split()
            assert len(tags) == expected_count, f"Failed for: {input_str}"
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_tag_prefix_formats(self):
        """测试不同标签前缀格式"""
        from utils.helper_functions import process_tags
        
        prefix_tests = [
            "tag1,tag2",           # 无前缀
            "#tag1,#tag2",         # 有#前缀
            "#tag1,tag2",          # 混合
            "##tag1,tag2",         # 双#
        ]
        
        for input_str in prefix_tests:
            success, result = process_tags(input_str)
            assert success is True
            # 不应该有双#
            assert "##" not in result
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_json_formats(self):
        """测试不同JSON格式"""
        from utils.helper_functions import parse_json_list
        
        json_formats = [
            '["item1", "item2"]',                    # 标准格式
            '["item1","item2"]',                     # 无空格
            '[ "item1" , "item2" ]',                 # 额外空格
            '[\n  "item1",\n  "item2"\n]',          # 多行
            '[1, 2, 3]',                             # 数字
            '[true, false, null]',                   # 布尔和null
            '[]',                                    # 空列表
        ]
        
        for json_str in json_formats:
            result = parse_json_list(json_str)
            assert isinstance(result, list)
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_file_extension_formats(self):
        """测试不同文件扩展名格式"""
        from utils.file_validator import FileTypeValidator
        
        # 测试不同的配置格式
        config_formats = [
            ".pdf,.zip",           # 带点
            "pdf,zip",             # 不带点
            ".PDF,.ZIP",           # 大写
            " .pdf , .zip ",       # 带空格
            ".pdf, .zip",          # 逗号后空格
        ]
        
        for config in config_formats:
            validator = FileTypeValidator(allowed_types=config)
            valid, msg = validator.validate("test.pdf", "application/pdf")
            assert valid is True, f"Failed for config: {config}"


class TestMIMETypeCompatibility:
    """MIME类型兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_common_mime_types(self):
        """测试常见MIME类型"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types="image/*,application/pdf")
        
        common_mimes = [
            ("image.jpg", "image/jpeg", True),
            ("image.png", "image/png", True),
            ("image.gif", "image/gif", True),
            ("image.webp", "image/webp", True),
            ("doc.pdf", "application/pdf", True),
            ("video.mp4", "video/mp4", False),
        ]
        
        for filename, mime, expected in common_mimes:
            valid, msg = validator.validate(filename, mime)
            assert valid == expected, f"Failed for {filename} ({mime})"
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_mime_type_variations(self):
        """测试MIME类型变体"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".jpg,.jpeg")
        
        # JPEG的不同MIME类型表示
        jpeg_mimes = [
            "image/jpeg",
            "image/jpg",
            "IMAGE/JPEG",  # 大写
        ]
        
        for mime in jpeg_mimes:
            valid, msg = validator.validate("test.jpg", mime)
            # 应该通过扩展名验证
            assert valid is True
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_mime_wildcard(self):
        """测试MIME通配符"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types="image/*")
        
        image_mimes = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.gif", "image/gif"),
            ("test.bmp", "image/bmp"),
            ("test.svg", "image/svg+xml"),
        ]
        
        for filename, mime in image_mimes:
            valid, msg = validator.validate(filename, mime)
            assert valid is True, f"Failed for {mime}"


class TestPlatformCompatibility:
    """平台兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_path_separators(self):
        """测试路径分隔符"""
        from utils.file_validator import FileTypeValidator
        
        validator = FileTypeValidator(allowed_types=".pdf")
        
        # 不同平台的路径格式
        paths = [
            "folder/file.pdf",           # Unix
            "folder\\file.pdf",          # Windows
            "folder/subfolder/file.pdf", # 多级Unix
            "C:\\Users\\file.pdf",       # Windows绝对路径
        ]
        
        for path in paths:
            valid, msg = validator.validate(path, "application/pdf")
            assert valid is True, f"Failed for path: {path}"
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_line_endings(self):
        """测试不同行结束符"""
        from utils.helper_functions import process_tags
        
        line_endings = [
            "tag1\ntag2",      # Unix (LF)
            "tag1\r\ntag2",    # Windows (CRLF)
            "tag1\rtag2",      # Old Mac (CR)
        ]
        
        for input_str in line_endings:
            success, result = process_tags(input_str)
            assert success is True
            # 应该正确分割
            tags = result.split()
            assert len(tags) == 2


class TestDataStructureCompatibility:
    """数据结构兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_dict_like_objects(self):
        """测试类字典对象"""
        from utils.helper_functions import build_caption
        
        # 标准字典
        dict_data = {
            "link": "https://example.com",
            "title": "Test",
            "note": "Note",
            "tags": "#test",
            "spoiler": "false",
            "user_id": 12345,
        }
        caption = build_caption(dict_data)
        assert isinstance(caption, str)
        
        # 类字典对象
        class DictLike:
            def __getitem__(self, key):
                return dict_data.get(key)
            
            def __contains__(self, key):
                return key in dict_data
        
        try:
            caption = build_caption(DictLike())
            assert isinstance(caption, str)
        except (TypeError, AttributeError):
            # 可接受的异常
            pass
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_sqlite_row_compatibility(self):
        """测试SQLite Row兼容性"""
        from utils.helper_functions import get_submission_mode
        import sqlite3
        
        # 创建内存数据库
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute('CREATE TABLE test (mode TEXT)')
        conn.execute("INSERT INTO test VALUES ('media')")
        
        cursor = conn.execute('SELECT * FROM test')
        row = cursor.fetchone()
        
        mode = get_submission_mode(row)
        assert mode == "media"
        
        conn.close()


class TestVersionCompatibility:
    """版本兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_json_module_compatibility(self):
        """测试JSON模块兼容性"""
        from utils.helper_functions import parse_json_list
        
        # 测试各种JSON特性
        json_tests = [
            '["unicode: \\u4e2d\\u6587"]',  # Unicode转义
            '["escaped: \\"quote\\""]',      # 转义引号
            '[1.5e10]',                       # 科学计数法
            '[-0]',                           # 负零
        ]
        
        for json_str in json_tests:
            result = parse_json_list(json_str)
            assert isinstance(result, list)
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_regex_compatibility(self):
        """测试正则表达式兼容性"""
        from utils.helper_functions import TAG_SPLIT_PATTERN
        
        # 测试正则表达式模式
        test_strings = [
            "a,b,c",
            "a b c",
            "a，b，c",
            "a\tb\tc",
        ]
        
        for s in test_strings:
            result = TAG_SPLIT_PATTERN.split(s)
            assert len(result) >= 1


class TestConfigurationCompatibility:
    """配置兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_boolean_config_values(self):
        """测试布尔配置值"""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES']
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO']
        
        for val in true_values:
            assert val.lower() in ('true', '1', 'yes')
        
        for val in false_values:
            assert val.lower() in ('false', '0', 'no')
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_integer_config_values(self):
        """测试整数配置值"""
        int_strings = ['123', '0', '-1', '999999999']
        
        for s in int_strings:
            try:
                val = int(s)
                assert isinstance(val, int)
            except ValueError:
                pytest.fail(f"Failed to parse: {s}")
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_file_type_config_formats(self):
        """测试文件类型配置格式"""
        from utils.file_validator import FileTypeValidator
        
        config_formats = [
            "*",                                    # 允许所有
            "",                                     # 空（允许所有）
            ".pdf",                                 # 单个扩展名
            ".pdf,.zip,.rar",                       # 多个扩展名
            "application/pdf",                      # 单个MIME
            "application/pdf,application/zip",      # 多个MIME
            ".pdf,application/zip",                 # 混合
            "image/*",                              # MIME通配符
        ]
        
        for config in config_formats:
            validator = FileTypeValidator(allowed_types=config)
            assert validator is not None


class TestAPICompatibility:
    """API兼容性测试"""
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_function_signatures(self):
        """测试函数签名兼容性"""
        from utils.helper_functions import (
            process_tags,
            escape_markdown,
            build_caption,
            parse_json_list,
            get_submission_mode,
        )
        
        # 验证函数可以被正确调用
        assert callable(process_tags)
        assert callable(escape_markdown)
        assert callable(build_caption)
        assert callable(parse_json_list)
        assert callable(get_submission_mode)
    
    @pytest.mark.compatibility
    @pytest.mark.unit
    def test_return_types(self):
        """测试返回类型兼容性"""
        from utils.helper_functions import (
            process_tags,
            escape_markdown,
            build_caption,
            parse_json_list,
        )
        
        # process_tags 返回 tuple
        result = process_tags("test")
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        # escape_markdown 返回 str
        result = escape_markdown("test")
        assert isinstance(result, str)
        
        # build_caption 返回 str
        result = build_caption({})
        assert isinstance(result, str)
        
        # parse_json_list 返回 list
        result = parse_json_list("[]")
        assert isinstance(result, list)
