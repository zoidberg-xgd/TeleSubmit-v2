"""
处理器模块
"""
# 基础命令和会话控制
from handlers.mode_selection import start, select_mode
from handlers.command_handlers import cancel
from handlers.command_handlers import debug, catch_all

# 为了兼容性创建别名
help_command = debug  # 临时用debug函数代替help_command
settings = debug      # 临时用debug函数代替settings
settings_callback = lambda update, context: None  # 空函数作为settings_callback

# 媒体和文档处理
handle_image = debug  # 临时替代
done_image = lambda update, context: None
handle_document = debug  # 临时替代
done_document = lambda update, context: None

# 文本处理
handle_text = debug  # 临时替代
collect_extra = lambda update, context: None

# 媒体处理函数
from handlers.media_handlers import handle_media, done_media, prompt_media, skip_media, switch_to_doc_mode

# 文档处理函数
from handlers.document_handlers import handle_doc, done_doc, prompt_doc

# 提交处理函数
from handlers.submit_handlers import (
    handle_tag, 
    handle_link, 
    handle_title, 
    handle_note, 
    handle_spoiler,
    skip_optional_link,
    skip_optional_title,
    skip_optional_note
)

# 投稿处理
from handlers.publish import publish_submission