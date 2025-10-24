#!/usr/bin/env python3
"""
清除测试数据 - 只删除测试用户的帖子
"""
import sqlite3
from datetime import datetime

def main():
    conn = sqlite3.connect('data/submissions.db')
    c = conn.cursor()
    
    print('='*80)
    print('🔍 查找测试数据')
    print('='*80)
    
    # 查找可能的测试数据
    test_users = ['testuser', 'test', 'vtide']  # 可以自定义测试用户列表
    
    for user in test_users:
        c.execute('''
            SELECT message_id, username, title, tags, publish_time 
            FROM published_posts 
            WHERE username = ?
            ORDER BY publish_time DESC
        ''', (user,))
        posts = c.fetchall()
        
        if posts:
            print(f'\n👤 用户: {user} ({len(posts)} 条帖子)')
            print('-'*80)
            for post in posts:
                msg_id, username, title, tags, pub_time = post
                time_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M:%S') if pub_time else 'N/A'
                print(f'  ID: {msg_id:4} | 标题: {title or "N/A":30} | 标签: {tags or "无":20} | {time_str}')
    
    # 显示所有数据统计
    print('\n' + '='*80)
    c.execute('SELECT COUNT(*) FROM published_posts')
    total_count = c.fetchone()[0]
    
    # 统计测试用户的帖子数
    placeholders = ','.join(['?'] * len(test_users))
    c.execute(f'SELECT COUNT(*) FROM published_posts WHERE username IN ({placeholders})', test_users)
    test_count = c.fetchone()[0]
    
    print(f'📊 数据统计:')
    print(f'   总帖子数: {total_count}')
    print(f'   测试帖子数: {test_count}')
    print(f'   保留帖子数: {total_count - test_count}')
    print('='*80)
    
    if test_count > 0:
        response = input(f'\n确认删除这 {test_count} 条测试数据吗？(输入 YES 确认): ')
        
        if response == 'YES':
            c.execute(f'DELETE FROM published_posts WHERE username IN ({placeholders})', test_users)
            deleted = c.rowcount
            conn.commit()
            
            print(f'\n✅ 已成功删除 {deleted} 条测试数据')
            
            # 显示剩余数据
            c.execute('SELECT COUNT(*) FROM published_posts')
            remaining = c.fetchone()[0]
            print(f'✅ 剩余 {remaining} 条帖子')
        else:
            print('\n❌ 操作已取消')
    else:
        print('\n✨ 未找到测试数据')
    
    conn.close()

if __name__ == '__main__':
    main()

