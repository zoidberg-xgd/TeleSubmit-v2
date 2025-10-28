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
                # 将 update 放入队列处理
                await self.application.update_queue.put(update)
                logger.debug(f"收到 Webhook 更新: {update.update_id}")
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
        success = await application.bot.set_webhook(
            url=full_webhook_url,
            secret_token=secret_token,
            allowed_updates=None,  # 接收所有类型的更新
            drop_pending_updates=True
        )
        
        if success:
            logger.info(f"✅ Webhook 设置成功: {full_webhook_url}")
            logger.info(f"✅ Secret Token: {secret_token}")
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

