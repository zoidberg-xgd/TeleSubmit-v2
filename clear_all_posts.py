#!/usr/bin/env python3
"""
清空所有已发布的帖子数据
⚠️ 警告：此操作将删除所有已发布的帖子，无法恢复！
"""
import sqlite3
import sys

def main():
    print('='*80)
    print('⚠️  警告：即将删除所有已发布的帖子数据')
    print('='*80)
    
    # 显示当前数据
    conn = sqlite3.connect('data/submissions.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM published_posts')
    count = c.fetchone()[0]
    
    print(f'\n当前数据库中有 {count} 条已发布的帖子')
    
    # 显示最近的几条
    c.execute('SELECT message_id, username, title, tags FROM published_posts ORDER BY publish_time DESC LIMIT 5')
    posts = c.fetchall()
    
    if posts:
        print('\n最近的帖子:')
        print('-'*80)
        for post in posts:
            msg_id, username, title, tags = post
            print(f'  消息ID: {msg_id}, 用户: {username}, 标题: {title or "N/A"}, 标签: {tags or "无"}')
    
    print('\n' + '='*80)
    response = input('确认要删除所有数据吗？(输入 YES 确认): ')
    
    if response == 'YES':
        c.execute('DELETE FROM published_posts')
        conn.commit()
        
        # 重置自增ID
        c.execute('DELETE FROM sqlite_sequence WHERE name="published_posts"')
        conn.commit()
        
        print('\n✅ 已成功删除所有已发布的帖子数据')
        print('✅ 数据库已重置')
    else:
        print('\n❌ 操作已取消')
    
    conn.close()

if __name__ == '__main__':
    main()

