#!/usr/bin/env python3
"""
标签诊断工具 - 检查数据库中的所有标签
"""
import sqlite3
import json

def main():
    conn = sqlite3.connect('data/submissions.db')
    c = conn.cursor()
    
    # 获取所有带标签的帖子
    c.execute('''
        SELECT message_id, username, title, tags, publish_time 
        FROM published_posts 
        WHERE tags IS NOT NULL 
        ORDER BY publish_time DESC
    ''')
    posts = c.fetchall()
    
    print('='*100)
    print('🔍 标签详细诊断报告')
    print('='*100)
    print(f'\n📊 总计: {len(posts)} 条带标签的投稿\n')
    
    # 详细列出每个帖子的标签
    print('📋 帖子详情:')
    print('-'*100)
    print(f'{"ID":<8} | {"用户":<15} | {"标题":<25} | {"标签":<35}')
    print('-'*100)
    
    all_tags = []
    for post in posts:
        msg_id, username, title, tags_str, _ = post
        title_display = (title[:23] + '..') if title and len(title) > 25 else (title or 'N/A')
        username_display = username or 'N/A'
        
        print(f'{msg_id:<8} | {username_display:<15} | {title_display:<25} | {tags_str}')
        
        # 解析标签
        try:
            tags = json.loads(tags_str)
        except:
            tags = tags_str.split() if tags_str else []
        
        all_tags.extend(tags)
    
    # 统计标签
    print('\n' + '='*100)
    print('📈 标签统计 (所有标签):')
    print('='*100)
    
    tag_counts = {}
    tag_sources = {}  # 记录每个标签来自哪些帖子
    
    for post in posts:
        msg_id, username, title, tags_str, _ = post
        try:
            tags = json.loads(tags_str)
        except:
            tags = tags_str.split() if tags_str else []
        
        for tag in tags:
            # 移除 # 前缀进行统计
            tag_clean = tag.lstrip('#')
            if tag_clean:
                tag_counts[tag_clean] = tag_counts.get(tag_clean, 0) + 1
                if tag_clean not in tag_sources:
                    tag_sources[tag_clean] = []
                tag_sources[tag_clean].append({
                    'message_id': msg_id,
                    'username': username,
                    'title': title or 'N/A'
                })
    
    # 按使用次数排序
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    for idx, (tag, count) in enumerate(sorted_tags, 1):
        if idx <= 3:
            emoji = '🔥'
        elif idx <= 10:
            emoji = '⭐'
        else:
            emoji = '📌'
        
        print(f'\n{emoji} #{tag} (使用 {count} 次)')
        print(f'   来源帖子:')
        for source in tag_sources[tag]:
            print(f'     - 消息ID: {source["message_id"]}, 用户: {source["username"]}, 标题: {source["title"]}')
    
    # 检查异常标签
    print('\n' + '='*100)
    print('⚠️  异常检查:')
    print('='*100)
    
    issues = []
    for tag in tag_counts.keys():
        # 检查是否有特殊字符
        if any(char in tag for char in ['<', '>', '&', '"', "'"]):
            issues.append(f'标签 "#{tag}" 包含特殊字符')
        # 检查是否有多余空格
        if tag != tag.strip():
            issues.append(f'标签 "#{tag}" 包含多余空格')
        # 检查是否过长
        if len(tag) > 30:
            issues.append(f'标签 "#{tag}" 长度超过30字符 (长度: {len(tag)})')
    
    if issues:
        for issue in issues:
            print(f'⚠️  {issue}')
    else:
        print('✅ 未发现异常标签')
    
    print('\n' + '='*100)
    print('✨ 诊断完成')
    print('='*100)
    
    conn.close()

if __name__ == '__main__':
    main()

