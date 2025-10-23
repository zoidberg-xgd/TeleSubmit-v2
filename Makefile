.PHONY: help build up down start stop restart logs status clean backup

# 默认目标
help:
	@echo "TeleSubmit Docker 管理命令"
	@echo ""
	@echo "使用方法: make [命令]"
	@echo ""
	@echo "可用命令:"
	@echo "  deploy      - 一键部署（首次使用）"
	@echo "  build       - 构建 Docker 镜像"
	@echo "  up          - 启动容器（后台运行）"
	@echo "  down        - 停止并删除容器"
	@echo "  start       - 启动已停止的容器"
	@echo "  stop        - 停止容器"
	@echo "  restart     - 重启容器"
	@echo "  logs        - 查看实时日志"
	@echo "  logs-tail   - 查看最近100行日志"
	@echo "  status      - 查看容器状态"
	@echo "  shell       - 进入容器 shell"
	@echo "  backup      - 备份数据"
	@echo "  clean       - 清理容器和镜像"
	@echo "  update      - 更新到最新版本"
	@echo ""

# 一键部署
deploy:
	@echo "🚀 开始部署..."
	@./deploy.sh

# 构建镜像
build:
	@echo "🔨 构建 Docker 镜像..."
	docker-compose build

# 启动容器
up:
	@echo "⬆️  启动容器..."
	docker-compose up -d
	@echo "✅ 容器已启动"

# 停止并删除容器
down:
	@echo "⬇️  停止容器..."
	docker-compose down
	@echo "✅ 容器已停止"

# 启动已停止的容器
start:
	@echo "▶️  启动容器..."
	docker-compose start
	@echo "✅ 容器已启动"

# 停止容器
stop:
	@echo "⏸️  停止容器..."
	docker-compose stop
	@echo "✅ 容器已停止"

# 重启容器
restart:
	@echo "🔄 重启容器..."
	docker-compose restart
	@echo "✅ 容器已重启"

# 查看实时日志
logs:
	@echo "📋 查看实时日志（按 Ctrl+C 退出）..."
	docker-compose logs -f

# 查看最近100行日志
logs-tail:
	@echo "📋 查看最近100行日志..."
	docker-compose logs --tail=100

# 查看容器状态
status:
	@echo "📊 容器状态:"
	@docker-compose ps
	@echo ""
	@echo "💻 资源使用:"
	@docker stats --no-stream telesubmit-bot 2>/dev/null || echo "容器未运行"

# 进入容器 shell
shell:
	@echo "🐚 进入容器 shell（输入 exit 退出）..."
	docker-compose exec telesubmit /bin/bash

# 备份数据
backup:
	@echo "💾 备份数据..."
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz config.ini data/ logs/ 2>/dev/null || true
	@echo "✅ 备份完成: backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz"

# 清理容器和镜像
clean:
	@echo "🧹 清理容器和镜像..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ 清理完成"

# 更新到最新版本
update:
	@echo "🔄 更新到最新版本..."
	@make backup
	@echo "⬇️  拉取最新代码..."
	git pull
	@echo "🔨 重新构建镜像..."
	docker-compose build --no-cache
	@echo "🚀 重启容器..."
	docker-compose up -d
	@echo "✅ 更新完成"
	@echo ""
	@echo "📋 查看日志确认运行正常:"
	@echo "   make logs"

