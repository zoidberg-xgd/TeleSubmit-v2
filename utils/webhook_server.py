"""
Webhook 服务器模块
用于接收 Telegram 的 Webhook 推送
"""
import os
import logging
import secrets
from aiohttp import web
from telegram import Update

logger = logging.getLogger(__name__)


class WebhookServer:
    """Webhook 服务器类"""
    
    def __init__(self, application, port: int, path: str, secret_token: str = None):
        """
        初始化 Webhook 服务器
        
        Args:
            application: telegram.ext.Application 实例
            port: 监听端口
            path: Webhook 路径
            secret_token: 可选的密钥 token，用于验证请求来源
        """
        self.application = application
        self.port = port
        self.path = path
        self.secret_token = secret_token or secrets.token_urlsafe(32)
        self.web_app = None
        self.runner = None
        
        logger.info(f"Webhook 服务器初始化: 端口={port}, 路径={path}")
        if not secret_token:
            logger.info(f"已自动生成 Secret Token: {self.secret_token}")
    
    async def webhook_handler(self, request: web.Request) -> web.Response:
        """
        处理 Webhook 请求
        
        Args:
            request: aiohttp Request 对象
            
        Returns:
            web.Response: HTTP 响应
        """
        # 验证 Secret Token（如果设置）
        if self.secret_token:
            request_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
            if request_token != self.secret_token:
                logger.warning(f"收到未授权的 Webhook 请求，Token 不匹配")
                return web.Response(status=401, text="Unauthorized")
        
        try:
            # 获取请求体
            data = await request.json()
            
            # 创建 Update 对象
            update = Update.de_json(data, self.application.bot)
            
            if update:
                # 记录更新类型（特别是频道消息）
                update_types = []
                if update.message:
                    update_types.append("message")
                if update.edited_message:
                    update_types.append("edited_message")
                if update.channel_post:
                    update_types.append("channel_post")
                if update.edited_channel_post:
                    update_types.append("edited_channel_post")
                if update.callback_query:
                    update_types.append("callback_query")
                if update.inline_query:
                    update_types.append("inline_query")
                
                update_type_str = ", ".join(update_types) if update_types else "unknown"
                
                # 如果是频道消息，使用info级别日志
                if update.channel_post or update.edited_channel_post:
                    logger.info(f"📢 收到频道消息更新: update_id={update.update_id}, type={update_type_str}")
                    if update.channel_post:
                        logger.info(f"   频道消息ID: {update.channel_post.message_id}, chat_id: {update.channel_post.chat.id if update.channel_post.chat else 'unknown'}")
                    if update.edited_channel_post:
                        logger.info(f"   编辑的频道消息ID: {update.edited_channel_post.message_id}, chat_id: {update.edited_channel_post.chat.id if update.edited_channel_post.chat else 'unknown'}")
                else:
                    logger.debug(f"收到 Webhook 更新: update_id={update.update_id}, type={update_type_str}")
                
                # 将 update 放入队列处理
                await self.application.update_queue.put(update)
            else:
                logger.warning(f"无法解析 Webhook 数据: {data}")
            
            return web.Response(status=200, text="OK")
            
        except Exception as e:
            logger.error(f"处理 Webhook 请求失败: {e}", exc_info=True)
            return web.Response(status=500, text="Internal Server Error")
    
    async def health_handler(self, request: web.Request) -> web.Response:
        """
        健康检查端点
        
        Args:
            request: aiohttp Request 对象
            
        Returns:
            web.Response: HTTP 响应
        """
        return web.Response(status=200, text="OK")
    
    async def start(self):
        """启动 Webhook 服务器"""
        self.web_app = web.Application()
        
        # 注册路由
        self.web_app.router.add_post(self.path, self.webhook_handler)
        self.web_app.router.add_get('/health', self.health_handler)
        
        # 创建并启动 runner
        self.runner = web.AppRunner(self.web_app)
        await self.runner.setup()
        
        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"✅ Webhook 服务器已启动: http://0.0.0.0:{self.port}{self.path}")
        logger.info(f"✅ 健康检查端点: http://0.0.0.0:{self.port}/health")
    
    async def stop(self):
        """停止 Webhook 服务器"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Webhook 服务器已停止")


async def setup_webhook(application, webhook_url: str, webhook_path: str, secret_token: str):
    """
    设置 Telegram Webhook
    
    Args:
        application: telegram.ext.Application 实例
        webhook_url: 外部访问的 Webhook URL
        webhook_path: Webhook 路径
        secret_token: Secret Token
    """
    full_webhook_url = f"{webhook_url.rstrip('/')}{webhook_path}"
    
    try:
        # 删除现有 webhook（如果有）
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("已删除现有 Webhook")
        
        # 设置新的 webhook
        # 明确指定需要接收的更新类型，包括频道消息
        allowed_updates = [
            "message",           # 普通消息
            "edited_message",    # 编辑的消息
            "channel_post",      # 频道消息（重要！）
            "edited_channel_post",  # 编辑的频道消息
            "callback_query",   # 回调查询
            "inline_query",      # 内联查询
        ]
        success = await application.bot.set_webhook(
            url=full_webhook_url,
            secret_token=secret_token,
            allowed_updates=allowed_updates,  # 明确指定接收频道消息
            drop_pending_updates=True
        )
        
        if success:
            logger.info(f"✅ Webhook 设置成功: {full_webhook_url}")
            logger.info(f"✅ Secret Token: {secret_token}")
            logger.info(f"✅ Allowed Updates: {', '.join(allowed_updates)}")
            
            # 验证 webhook 信息
            try:
                webhook_info = await application.bot.get_webhook_info()
                logger.info(f"✅ Webhook 验证信息:")
                logger.info(f"   URL: {webhook_info.url}")
                logger.info(f"   待处理更新数: {webhook_info.pending_update_count}")
                logger.info(f"   Allowed Updates: {webhook_info.allowed_updates}")
                if webhook_info.allowed_updates:
                    has_channel_post = "channel_post" in webhook_info.allowed_updates
                    has_edited_channel_post = "edited_channel_post" in webhook_info.allowed_updates
                    logger.info(f"   ✅ 包含 channel_post: {has_channel_post}")
                    logger.info(f"   ✅ 包含 edited_channel_post: {has_edited_channel_post}")
                    if not (has_channel_post and has_edited_channel_post):
                        logger.warning("⚠️  警告: Webhook 配置中缺少频道消息类型！")
                else:
                    logger.warning("⚠️  警告: Webhook 配置中没有 allowed_updates，将接收所有更新类型")
            except Exception as e:
                logger.warning(f"无法获取 Webhook 信息: {e}")
            
            return True
        else:
            logger.error(f"❌ Webhook 设置失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 设置 Webhook 时发生错误: {e}", exc_info=True)
        return False


async def delete_webhook(application):
    """
    删除 Telegram Webhook
    
    Args:
        application: telegram.ext.Application 实例
    """
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook 已删除")
        return True
    except Exception as e:
        logger.error(f"❌ 删除 Webhook 时发生错误: {e}", exc_info=True)
        return False

