#!/usr/bin/env python3
"""
标签云功能测试脚本
用于验证标签云和标签搜索功能是否正常工作
"""

import asyncio
import aiosqlite
import json
from utils.search_engine import get_search_engine


async def test_tag_cloud():
    """测试标签云统计功能"""
    print("=" * 60)
    print("测试1: 标签云统计功能")
    print("=" * 60)
    
    conn = await aiosqlite.connect('data/submissions.db')
    conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    
    # 获取所有帖子的标签
    await cursor.execute('SELECT tags FROM published_posts WHERE tags IS NOT NULL')
    posts = await cursor.fetchall()
    
    print(f'\n📊 找到 {len(posts)} 条带标签的投稿\n')
    
    # 统计标签使用次数
    tag_counts = {}
    for post in posts:
        try:
            # 尝试作为 JSON 解析（兼容旧数据）
            tags = json.loads(post['tags'])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        except:
            # 如果不是 JSON，按空格分割（当前格式：'#测试 #标签2'）
            tags_text = post['tags']
            if tags_text:
                tags = tags_text.split()
                for tag in tags:
                    # 移除 # 前缀，统一处理
                    tag_clean = tag.lstrip('#')
                    if tag_clean:
                        tag_counts[tag_clean] = tag_counts.get(tag_clean, 0) + 1
    
    if not tag_counts:
        print('❌ 没有标签数据')
        return False
    else:
        # 按使用次数排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 构建标签云消息
        print(f'🏷️ 标签云 TOP {len(sorted_tags)}\n')
        
        for idx, (tag, count) in enumerate(sorted_tags, 1):
            # 使用不同的表情符号表示热度
            if idx <= 3:
                emoji = '🔥'
            elif idx <= 10:
                emoji = '⭐'
            else:
                emoji = '📌'
            
            print(f'{emoji} #{tag} ({count})')
        
        print(f'\n💡 使用 /search #{sorted_tags[0][0]} 搜索该标签的帖子')
    
    await conn.close()
    return True


async def test_tag_search():
    """测试标签搜索功能"""
    print("\n" + "=" * 60)
    print("测试2: 标签搜索功能")
    print("=" * 60)
    
    # 获取搜索引擎
    try:
        engine = get_search_engine()
    except Exception as e:
        print(f'\n❌ 搜索引擎初始化失败: {e}')
        print('提示: 请先运行 "python3 migrate_to_search.py" 初始化搜索索引')
        return False
    
    # 测试搜索不同的标签
    test_tags = ['编程', 'Python', 'Java']
    
    for tag in test_tags:
        # 标准化标签：移除#并转换为小写（与实际搜索行为一致）
        normalized_tag = tag.lstrip('#').lower()
        print(f'\n🔍 搜索标签: "{tag}" (标准化为: "{normalized_tag}")')
        try:
            result = engine.search(
                query_str=normalized_tag,
                page_num=1,
                page_len=10,
                tag_filter=normalized_tag,
                sort_by='publish_time'
            )
            
            print(f'  找到 {result.total_results} 个结果')
            
            if result.hits:
                for hit in result.hits[:3]:  # 只显示前3个
                    print(f'    - [{hit.message_id}] {hit.title or "无标题"} | 标签: {hit.tags}')
            else:
                print(f'    ℹ️  没有找到带有标签 "#{tag}" 的投稿')
                
        except Exception as e:
            print(f'  ❌ 搜索失败: {e}')
            return False
    
    return True


async def test_database_structure():
    """测试数据库结构"""
    print("\n" + "=" * 60)
    print("测试3: 数据库结构检查")
    print("=" * 60)
    
    try:
        conn = await aiosqlite.connect('data/submissions.db')
        cursor = await conn.cursor()
        
        # 检查表是否存在
        await cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        print(f'\n📋 数据库表: {", ".join([t[0] for t in tables])}')
        
        # 检查 published_posts 表结构
        await cursor.execute('PRAGMA table_info(published_posts)')
        columns = await cursor.fetchall()
        print(f'\n📊 published_posts 表字段:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')
        
        # 统计投稿数量
        await cursor.execute('SELECT COUNT(*) FROM published_posts')
        count = await cursor.fetchone()
        print(f'\n📈 总投稿数: {count[0]}')
        
        # 显示示例数据
        await cursor.execute('SELECT message_id, title, tags FROM published_posts LIMIT 3')
        posts = await cursor.fetchall()
        if posts:
            print(f'\n📝 示例投稿:')
            for post in posts:
                print(f'  消息ID: {post[0]}')
                print(f'  标题: {post[1] or "无标题"}')
                print(f'  标签: {post[2]}')
                print()
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f'\n❌ 数据库检查失败: {e}')
        return False


async def main():
    """主测试函数"""
    print("\n" + "🔍 标签云功能测试".center(60, "="))
    print()
    
    results = []
    
    # 运行所有测试
    results.append(("数据库结构检查", await test_database_structure()))
    results.append(("标签云统计", await test_tag_cloud()))
    results.append(("标签搜索", await test_tag_search()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f'{name}: {status}')
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！标签云功能工作正常。")
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())

