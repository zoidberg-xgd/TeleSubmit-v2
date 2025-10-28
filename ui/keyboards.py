"""
现代化的键盘布局模块
提供各种场景的 InlineKeyboard 和 ReplyKeyboard
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


class Keyboards:
    """键盘布局管理器"""
    
    @staticmethod
    def main_menu():
        """主菜单键盘"""
        keyboard = [
            [
                KeyboardButton("📝 开始投稿"),
                KeyboardButton("📊 我的统计")
            ],
            [
                KeyboardButton("📋 我的投稿"),
                KeyboardButton("🔥 热门内容")
            ],
            [
                KeyboardButton("🔍 搜索"),
                KeyboardButton("🏷️ 标签云")
            ],
            [
                KeyboardButton("❓ 帮助"),
                KeyboardButton("ℹ️ 关于")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def admin_menu():
        """管理员菜单（与主菜单一致，保留兼容）"""
        return Keyboards.main_menu()
    
    @staticmethod
    def submission_confirm(session_id: int):
        """投稿确认键盘"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认发布", callback_data=f"submit_confirm_{session_id}"),
                InlineKeyboardButton("✏️ 修改内容", callback_data=f"submit_edit_{session_id}")
            ],
            [
                InlineKeyboardButton("🏷️ 添加标签", callback_data=f"submit_addtag_{session_id}"),
                InlineKeyboardButton("📎 添加媒体", callback_data=f"submit_media_{session_id}")
            ],
            [
                InlineKeyboardButton("❌ 取消投稿", callback_data=f"submit_cancel_{session_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def hot_posts_filter():
        """热门帖子筛选键盘"""
        keyboard = [
            [
                InlineKeyboardButton("📅 今天", callback_data="hot_filter_day"),
                InlineKeyboardButton("📅 本周", callback_data="hot_filter_week"),
                InlineKeyboardButton("📅 本月", callback_data="hot_filter_month")
            ],
            [
                InlineKeyboardButton("🔢 前10", callback_data="hot_limit_10"),
                InlineKeyboardButton("🔢 前20", callback_data="hot_limit_20"),
                InlineKeyboardButton("🔢 前30", callback_data="hot_limit_30")
            ],
            [
                InlineKeyboardButton("🔄 刷新", callback_data="hot_refresh")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def search_options():
        """搜索选项键盘"""
        keyboard = [
            [
                InlineKeyboardButton("📝 全文搜索", callback_data="search_fulltext"),
                InlineKeyboardButton("🏷️ 标签搜索", callback_data="search_tag")
            ],
            [
                InlineKeyboardButton("👤 我的投稿", callback_data="search_myposts"),
                InlineKeyboardButton("📅 按时间", callback_data="search_time")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def post_actions(post_id: int, user_id: int, is_owner: bool = False):
        """帖子操作键盘"""
        keyboard = []
        
        # 第一行：查看和分享
        row1 = [
            InlineKeyboardButton("👁️ 查看原帖", callback_data=f"view_post_{post_id}"),
            InlineKeyboardButton("📊 查看统计", callback_data=f"stats_post_{post_id}")
        ]
        keyboard.append(row1)
        
        # 第二行：用户相关操作
        if is_owner:
            row2 = [
                InlineKeyboardButton("🗑️ 删除", callback_data=f"delete_post_{post_id}"),
                InlineKeyboardButton("📝 编辑", callback_data=f"edit_post_{post_id}")
            ]
            keyboard.append(row2)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_panel():
        """已移除：返回到主菜单按钮（兼容旧回调）"""
        keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def blacklist_actions(user_id: int):
        """黑名单操作键盘"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 移除黑名单", callback_data=f"unblock_{user_id}"),
                InlineKeyboardButton("📊 查看详情", callback_data=f"userinfo_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="admin_blacklist")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def time_filter():
        """时间筛选键盘"""
        keyboard = [
            [
                InlineKeyboardButton("📅 今天", callback_data="time_day"),
                InlineKeyboardButton("📅 本周", callback_data="time_week")
            ],
            [
                InlineKeyboardButton("📅 本月", callback_data="time_month"),
                InlineKeyboardButton("📅 全部", callback_data="time_all")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(current_page: int, total_pages: int, prefix: str = "page"):
        """分页键盘"""
        keyboard = []
        
        # 页码按钮
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⏮️ 首页", callback_data=f"{prefix}_1"))
            nav_buttons.append(InlineKeyboardButton("◀️ 上页", callback_data=f"{prefix}_{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="page_info"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("▶️ 下页", callback_data=f"{prefix}_{current_page+1}"))
            nav_buttons.append(InlineKeyboardButton("⏭️ 末页", callback_data=f"{prefix}_{total_pages}"))
        
        keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def tag_cloud(tags: list, max_tags: int = 20):
        """标签云键盘"""
        keyboard = []
        row = []
        
        for i, (tag, count) in enumerate(tags[:max_tags]):
            # 根据使用频率设置 emoji
            if count >= 10:
                emoji = "🔥"
            elif count >= 5:
                emoji = "⭐"
            else:
                emoji = "🏷️"
            
            button = InlineKeyboardButton(
                f"{emoji} {tag} ({count})",
                callback_data=f"tag_search_{tag}"
            )
            row.append(button)
            
            # 每行2个标签
            if len(row) == 2 or i == len(tags) - 1:
                keyboard.append(row)
                row = []
        
        # 添加返回按钮
        keyboard.append([InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def yes_no(action: str, item_id: str = ""):
        """确认/取消键盘"""
        callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
        callback_no = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认", callback_data=callback_yes),
                InlineKeyboardButton("❌ 取消", callback_data=callback_no)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def remove_keyboard():
        """移除键盘"""
        return ReplyKeyboardRemove()


class QuickReplies:
    """快捷回复"""
    
    @staticmethod
    def submission_templates():
        """投稿模板快捷回复"""
        keyboard = [
            [KeyboardButton("📰 新闻资讯")],
            [KeyboardButton("💡 技巧分享")],
            [KeyboardButton("❓ 问题求助")],
            [KeyboardButton("🎉 活动公告")],
            [KeyboardButton("💬 日常闲聊")],
            [KeyboardButton("🔙 返回主菜单")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def common_tags():
        """常用标签快捷回复"""
        keyboard = [
            [KeyboardButton("#技术"), KeyboardButton("#教程")],
            [KeyboardButton("#新闻"), KeyboardButton("#资讯")],
            [KeyboardButton("#分享"), KeyboardButton("#推荐")],
            [KeyboardButton("#问答"), KeyboardButton("#讨论")],
            [KeyboardButton("✅ 完成"), KeyboardButton("❌ 取消")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

