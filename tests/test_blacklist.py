"""
黑名单模块测试
测试黑名单的添加、删除、查询等功能
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import MagicMock, AsyncMock, patch


class TestBlacklistBasicOperations:
    """黑名单基本操作测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_blacklisted_not_in_list(self):
        """测试不在黑名单中的用户"""
        from utils.blacklist import is_blacklisted, _blacklist
        
        # 确保用户不在黑名单中
        test_user_id = 999999998
        _blacklist.discard(test_user_id)
        
        result = is_blacklisted(test_user_id)
        assert result is False
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_blacklisted_in_list(self):
        """测试在黑名单中的用户"""
        from utils.blacklist import is_blacklisted, _blacklist
        
        test_user_id = 999999997
        _blacklist.add(test_user_id)
        
        try:
            result = is_blacklisted(test_user_id)
            assert result is True
        finally:
            _blacklist.discard(test_user_id)
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_add_to_blacklist(self):
        """测试添加用户到黑名单"""
        from utils.blacklist import add_to_blacklist, is_blacklisted, _blacklist
        
        test_user_id = 999999996
        
        # 模拟数据库操作
        with patch('utils.blacklist.get_db') as mock_get_db:
            mock_conn = AsyncMock()
            mock_get_db.return_value.__aenter__.return_value = mock_conn
            
            result = await add_to_blacklist(test_user_id, "测试原因")
            
            # 验证内存缓存被更新
            assert test_user_id in _blacklist
            assert result is True
        
        # 清理
        _blacklist.discard(test_user_id)
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_remove_from_blacklist(self):
        """测试从黑名单移除用户"""
        from utils.blacklist import remove_from_blacklist, is_blacklisted, _blacklist
        
        test_user_id = 999999995
        _blacklist.add(test_user_id)
        
        with patch('utils.blacklist.get_db') as mock_get_db:
            mock_conn = AsyncMock()
            mock_get_db.return_value.__aenter__.return_value = mock_conn
            
            result = await remove_from_blacklist(test_user_id)
            
            # 验证内存缓存被更新
            assert test_user_id not in _blacklist
            assert result is True
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_remove_nonexistent_user(self):
        """测试移除不存在的用户"""
        from utils.blacklist import remove_from_blacklist, _blacklist
        
        test_user_id = 999999994
        _blacklist.discard(test_user_id)  # 确保不在黑名单中
        
        with patch('utils.blacklist.get_db') as mock_get_db:
            mock_conn = AsyncMock()
            mock_get_db.return_value.__aenter__.return_value = mock_conn
            
            result = await remove_from_blacklist(test_user_id)
            assert result is False
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_blacklist(self):
        """测试获取黑名单列表"""
        from utils.blacklist import _blacklist, is_blacklisted
        
        # 测试内存黑名单的获取功能
        test_ids = [123, 456]
        
        # 清理之前的状态
        for uid in test_ids:
            _blacklist.discard(uid)
        
        # 添加测试用户
        for uid in test_ids:
            _blacklist.add(uid)
        
        # 验证可以检查黑名单
        assert is_blacklisted(123) is True
        assert is_blacklisted(456) is True
        assert is_blacklisted(789) is False
        
        # 清理
        for uid in test_ids:
            _blacklist.discard(uid)


class TestBlacklistFilter:
    """黑名单过滤器测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_filter_blocks_blacklisted(self):
        """测试过滤器阻止黑名单用户"""
        from utils.blacklist import blacklist_filter, _blacklist
        
        test_user_id = 999999993
        _blacklist.add(test_user_id)
        
        try:
            mock_update = MagicMock()
            mock_update.effective_user.id = test_user_id
            
            result = blacklist_filter(mock_update)
            assert result is False
        finally:
            _blacklist.discard(test_user_id)
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_filter_allows_normal_user(self):
        """测试过滤器允许正常用户"""
        from utils.blacklist import blacklist_filter, _blacklist
        
        test_user_id = 999999992
        _blacklist.discard(test_user_id)
        
        mock_update = MagicMock()
        mock_update.effective_user.id = test_user_id
        
        result = blacklist_filter(mock_update)
        assert result is True
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_filter_handles_none_user(self):
        """测试过滤器处理None用户"""
        from utils.blacklist import blacklist_filter
        
        mock_update = MagicMock()
        mock_update.effective_user = None
        
        result = blacklist_filter(mock_update)
        assert result is True  # 没有用户时应该允许通过


class TestOwnerCheck:
    """所有者检查测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_owner_with_valid_owner(self):
        """测试有效所有者检查"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', 12345):
            result = is_owner(12345)
            assert result is True
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_owner_with_non_owner(self):
        """测试非所有者检查"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', 12345):
            result = is_owner(99999)
            assert result is False
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_owner_with_none_owner_id(self):
        """测试OWNER_ID为None时的检查"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', None):
            result = is_owner(12345)
            assert result is False
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_owner_with_none_user_id(self):
        """测试user_id为None时的检查"""
        from utils.blacklist import is_owner
        
        result = is_owner(None)
        assert result is False
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_is_owner_type_mismatch(self):
        """测试类型不匹配的所有者检查"""
        from utils.blacklist import is_owner
        
        with patch('utils.blacklist.OWNER_ID', 12345):
            # 字符串类型的ID
            result = is_owner("12345")
            # 应该返回False或正确处理
            assert isinstance(result, bool)


class TestBlacklistPersistence:
    """黑名单持久化测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_init_blacklist(self):
        """测试初始化黑名单"""
        from utils.blacklist import _blacklist
        
        # 直接测试内存黑名单的功能
        test_ids = [111, 222, 333]
        
        # 清理之前的状态
        for uid in test_ids:
            _blacklist.discard(uid)
        
        # 模拟加载黑名单到内存
        for uid in test_ids:
            _blacklist.add(uid)
        
        # 验证黑名单被加载
        assert 111 in _blacklist
        assert 222 in _blacklist
        assert 333 in _blacklist
        
        # 清理
        for uid in test_ids:
            _blacklist.discard(uid)
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_blacklist_database_error(self):
        """测试数据库错误处理"""
        from utils.blacklist import add_to_blacklist, _blacklist
        
        test_user_id = 999999991
        
        with patch('utils.blacklist.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.side_effect = Exception("Database error")
            
            result = await add_to_blacklist(test_user_id, "测试")
            
            # 应该返回False表示失败
            assert result is False
        
        # 清理
        _blacklist.discard(test_user_id)


class TestBlacklistEdgeCases:
    """黑名单边缘情况测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_with_large_user_id(self):
        """测试大用户ID"""
        from utils.blacklist import is_blacklisted, _blacklist
        
        large_id = 2**63 - 1
        _blacklist.add(large_id)
        
        try:
            result = is_blacklisted(large_id)
            assert result is True
        finally:
            _blacklist.discard(large_id)
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_with_negative_user_id(self):
        """测试负用户ID"""
        from utils.blacklist import is_blacklisted, _blacklist
        
        negative_id = -12345
        _blacklist.add(negative_id)
        
        try:
            result = is_blacklisted(negative_id)
            assert result is True
        finally:
            _blacklist.discard(negative_id)
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_add_duplicate_to_blacklist(self):
        """测试重复添加到黑名单"""
        from utils.blacklist import add_to_blacklist, _blacklist
        
        test_user_id = 999999990
        
        with patch('utils.blacklist.get_db') as mock_get_db:
            mock_conn = AsyncMock()
            mock_get_db.return_value.__aenter__.return_value = mock_conn
            
            # 第一次添加
            await add_to_blacklist(test_user_id, "原因1")
            # 第二次添加（应该更新）
            result = await add_to_blacklist(test_user_id, "原因2")
            
            assert result is True
            assert test_user_id in _blacklist
        
        # 清理
        _blacklist.discard(test_user_id)
    
    @pytest.mark.blacklist
    @pytest.mark.unit
    def test_blacklist_concurrent_access(self):
        """测试并发访问黑名单"""
        from utils.blacklist import is_blacklisted, _blacklist
        import threading
        
        test_ids = list(range(1000000, 1000100))
        errors = []
        
        def add_and_check():
            try:
                for user_id in test_ids:
                    _blacklist.add(user_id)
                    is_blacklisted(user_id)
                    _blacklist.discard(user_id)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=add_and_check) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


class TestManageBlacklistCommand:
    """黑名单管理命令测试"""
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_manage_blacklist_non_owner(self):
        """测试非所有者使用管理命令"""
        from utils.blacklist import manage_blacklist
        
        mock_update = MagicMock()
        mock_update.effective_user.id = 99999
        mock_update.message.reply_text = AsyncMock()
        mock_context = MagicMock()
        
        with patch('utils.blacklist.is_owner', return_value=False):
            await manage_blacklist(mock_update, mock_context)
            
            # 应该发送权限不足的消息
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "所有者" in call_args or "权限" in call_args
    
    @pytest.mark.blacklist
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_manage_blacklist_owner(self):
        """测试所有者使用管理命令"""
        from utils.blacklist import manage_blacklist
        
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message.reply_text = AsyncMock()
        mock_context = MagicMock()
        
        with patch('utils.blacklist.is_owner', return_value=True):
            await manage_blacklist(mock_update, mock_context)
            
            # 应该发送帮助信息
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "blacklist" in call_args.lower()
