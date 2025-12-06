"""
数据库相关测试
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


class TestDatabaseInitialization:
    """数据库初始化测试"""
    
    @pytest.mark.database
    def test_database_creation(self, temp_dir):
        """测试数据库创建"""
        from unittest.mock import patch
        
        db_path = os.path.join(temp_dir, 'test.db')
        
        # 使用 patch 来设置测试数据库路径
        with patch('utils.database.SESSION_DB_PATH', db_path):
            from utils.database import initialize_database
            initialize_database()
            
            # 验证数据库文件已创建
            assert os.path.exists(db_path)
            
            # 验证数据库可以连接
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 验证表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            tables = cursor.fetchall()
            
            conn.close()
            
            # 应该有一些表被创建
            assert len(tables) > 0


class TestDatabaseOperations:
    """数据库操作测试"""
    
    @pytest.fixture
    def test_db(self, temp_dir):
        """创建测试数据库"""
        db_path = os.path.join(temp_dir, 'test_ops.db')
        conn = sqlite3.connect(db_path)
        
        # 创建测试表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                content TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        
        yield conn
        
        conn.close()
    
    @pytest.mark.database
    def test_insert_post(self, test_db):
        """测试插入帖子"""
        cursor = test_db.cursor()
        
        cursor.execute('''
            INSERT INTO test_posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (123456, '测试内容', '2024-01-01'))
        
        test_db.commit()
        
        # 验证插入成功
        cursor.execute('SELECT * FROM test_posts WHERE user_id = ?', (123456,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == 123456
        assert result[2] == '测试内容'
    
    @pytest.mark.database
    def test_query_post(self, test_db):
        """测试查询帖子"""
        # 插入测试数据
        test_db.execute('''
            INSERT INTO test_posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (123456, '测试内容', '2024-01-01'))
        test_db.commit()
        
        # 查询
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts WHERE user_id = ?', (123456,))
        result = cursor.fetchone()
        
        assert result[0] == '测试内容'
    
    @pytest.mark.database
    def test_update_post(self, test_db):
        """测试更新帖子"""
        # 插入测试数据
        test_db.execute('''
            INSERT INTO test_posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (123456, '原内容', '2024-01-01'))
        test_db.commit()
        
        # 更新
        test_db.execute('''
            UPDATE test_posts SET content = ?
            WHERE user_id = ?
        ''', ('新内容', 123456))
        test_db.commit()
        
        # 验证更新
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts WHERE user_id = ?', (123456,))
        result = cursor.fetchone()
        
        assert result[0] == '新内容'
    
    @pytest.mark.database
    def test_delete_post(self, test_db):
        """测试删除帖子"""
        # 插入测试数据
        test_db.execute('''
            INSERT INTO test_posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (123456, '测试内容', '2024-01-01'))
        test_db.commit()
        
        # 删除
        test_db.execute('DELETE FROM test_posts WHERE user_id = ?', (123456,))
        test_db.commit()
        
        # 验证删除
        cursor = test_db.cursor()
        cursor.execute('SELECT * FROM test_posts WHERE user_id = ?', (123456,))
        result = cursor.fetchone()
        
        assert result is None


class TestDatabaseEdgeCases:
    """数据库边界情况测试"""
    
    @pytest.fixture
    def test_db(self, temp_dir):
        """创建测试数据库"""
        db_path = os.path.join(temp_dir, 'test_edge.db')
        conn = sqlite3.connect(db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_posts (
                id INTEGER PRIMARY KEY,
                content TEXT
            )
        ''')
        conn.commit()
        
        yield conn
        
        conn.close()
    
    @pytest.mark.database
    def test_unicode_content(self, test_db):
        """测试 Unicode 内容"""
        unicode_text = "测试 🎉 テスト тест"
        
        test_db.execute('INSERT INTO test_posts (content) VALUES (?)', (unicode_text,))
        test_db.commit()
        
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts')
        result = cursor.fetchone()
        
        assert result[0] == unicode_text
    
    @pytest.mark.database
    def test_empty_content(self, test_db):
        """测试空内容"""
        test_db.execute('INSERT INTO test_posts (content) VALUES (?)', ('',))
        test_db.commit()
        
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts')
        result = cursor.fetchone()
        
        assert result[0] == ''
    
    @pytest.mark.database
    def test_null_content(self, test_db):
        """测试 NULL 内容"""
        test_db.execute('INSERT INTO test_posts (content) VALUES (?)', (None,))
        test_db.commit()
        
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts')
        result = cursor.fetchone()
        
        assert result[0] is None
    
    @pytest.mark.database
    def test_very_long_content(self, test_db):
        """测试超长内容"""
        long_content = "测试" * 10000
        
        test_db.execute('INSERT INTO test_posts (content) VALUES (?)', (long_content,))
        test_db.commit()
        
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts')
        result = cursor.fetchone()
        
        assert result[0] == long_content
        assert len(result[0]) == len(long_content)
    
    @pytest.mark.database
    def test_special_characters(self, test_db):
        """测试特殊字符"""
        special_text = "测试'引号\"双引号\\反斜杠\n换行\t制表"
        
        test_db.execute('INSERT INTO test_posts (content) VALUES (?)', (special_text,))
        test_db.commit()
        
        cursor = test_db.cursor()
        cursor.execute('SELECT content FROM test_posts')
        result = cursor.fetchone()
        
        assert result[0] == special_text


class TestDatabaseConcurrency:
    """数据库并发测试"""
    
    @pytest.mark.database
    @pytest.mark.slow
    def test_concurrent_writes(self, temp_dir):
        """测试并发写入"""
        import threading
        
        db_path = os.path.join(temp_dir, 'test_concurrent.db')
        
        def write_data(thread_id):
            conn = sqlite3.connect(db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_posts (
                    id INTEGER PRIMARY KEY,
                    thread_id INTEGER,
                    content TEXT
                )
            ''')
            
            for i in range(10):
                conn.execute(
                    'INSERT INTO test_posts (thread_id, content) VALUES (?, ?)',
                    (thread_id, f'Content {i}')
                )
            conn.commit()
            conn.close()
        
        # 创建多个线程
        threads = []
        for i in range(5):
            t = threading.Thread(target=write_data, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证数据
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM test_posts')
        count = cursor.fetchone()[0]
        conn.close()
        
        # 应该有 5 * 10 = 50 条记录
        assert count == 50
