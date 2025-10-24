#!/usr/bin/env python3
"""
根据消息ID删除指定的帖子
"""
import sqlite3
from datetime import datetime

def main():
    conn = sqlite3.connect('data/submissions.db')
    c = conn.cursor()
    
    print('='*80)
    print('📋 当前所有已发布的帖子')
    print('='*80)
    
    # 显示所有帖子
    c.execute('''
        SELECT message_id, username, title, tags, publish_time 
        FROM published_posts 
        ORDER BY publish_time DESC
    ''')
    posts = c.fetchall()
    
    print(f'\n{"ID":<6} | {"用户名":<15} | {"标题":<30} | {"标签":<25} | {"发布时间"}')
    print('-'*80)
    for post in posts:
        msg_id, username, title, tags, pub_time = post
        title_display = (title[:28] + '..') if title and len(title) > 30 else (title or 'N/A')
        tags_display = (tags[:23] + '..') if tags and len(tags) > 25 else (tags or '无')
        time_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M:%S') if pub_time else 'N/A'
        print(f'{msg_id:<6} | {username:<15} | {title_display:<30} | {tags_display:<25} | {time_str}')
    
    print('\n' + '='*80)
    print('请输入要删除的消息ID，多个ID用逗号分隔（例如：853,854,855）')
    print('或输入 "all" 删除所有帖子')
    ids_input = input('消息ID: ').strip()
    
    if not ids_input:
        print('❌ 未输入任何ID，操作已取消')
        conn.close()
        return
    
    if ids_input.lower() == 'all':
        response = input(f'\n⚠️  确认删除所有 {len(posts)} 条帖子吗？(输入 YES 确认): ')
        if response == 'YES':
            c.execute('DELETE FROM published_posts')
            deleted = c.rowcount
            conn.commit()
            print(f'\n✅ 已删除所有 {deleted} 条帖子')
        else:
            print('\n❌ 操作已取消')
        conn.close()
        return
    
    # 解析ID列表
    try:
        ids_to_delete = [int(id.strip()) for id in ids_input.split(',')]
    except ValueError:
        print('❌ ID格式错误，请输入数字')
        conn.close()
        return
    
    # 显示要删除的帖子
    print(f'\n将要删除以下 {len(ids_to_delete)} 条帖子:')
    print('-'*80)
    
    for msg_id in ids_to_delete:
        c.execute('''
            SELECT message_id, username, title, tags 
            FROM published_posts 
            WHERE message_id = ?
        ''', (msg_id,))
        post = c.fetchone()
        
        if post:
            print(f'  ✓ ID: {post[0]:4} | 用户: {post[1] or "N/A":15} | 标题: {post[2] or "N/A":30} | 标签: {post[3] or "无"}')
        else:
            print(f'  ✗ ID: {msg_id:4} | (不存在)')
    
    print('-'*80)
    response = input(f'\n确认删除吗？(输入 YES 确认): ')
    
    if response == 'YES':
        placeholders = ','.join(['?'] * len(ids_to_delete))
        c.execute(f'DELETE FROM published_posts WHERE message_id IN ({placeholders})', ids_to_delete)
        deleted = c.rowcount
        conn.commit()
        
        print(f'\n✅ 已成功删除 {deleted} 条帖子')
        
        # 显示剩余数据
        c.execute('SELECT COUNT(*) FROM published_posts')
        remaining = c.fetchone()[0]
        print(f'✅ 剩余 {remaining} 条帖子')
    else:
        print('\n❌ 操作已取消')
    
    conn.close()

if __name__ == '__main__':
    main()

