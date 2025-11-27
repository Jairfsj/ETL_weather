# Montreal Weather ETL Dashboard - Makefile

.PHONY: help build up down restart logs clean test lint format setup

# Default target
help: ## Show this help message
	@echo "Montreal Weather ETL Dashboard"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Development commands
setup: ## Setup development environment
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env file and add your OpenWeatherMap API key"

build: ## Build all services
	@echo "Building all services..."
	docker compose build

up: ## Start all services
	@echo "Starting all services..."
	docker compose up -d

down: ## Stop all services
	@echo "Stopping all services..."
	docker compose down

restart: ## Restart all services
	@echo "Restarting all services..."
	docker compose restart

logs: ## Show logs from all services
	docker compose logs -f

logs-rust: ## Show logs from Rust ETL service
	docker compose logs -f rust_etl

logs-python: ## Show logs from Python API service
	docker compose logs -f python_analytics

logs-db: ## Show logs from PostgreSQL
	docker compose logs -f postgres

# Production commands
prod-up: ## Start services in production mode
	@echo "Starting services in production mode..."
	docker compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
	docker compose -f docker-compose.prod.yml down

# Database commands
db-connect: ## Connect to PostgreSQL database
	docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

db-backup: ## Create database backup
	docker compose exec postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	docker compose exec -T postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < ${FILE}

# Development commands
format: ## Format code (Rust)
	cd rust_etl && cargo fmt

lint: ## Lint code (Rust)
	cd rust_etl && cargo clippy -- -D warnings

test: ## Run tests (Rust)
	cd rust_etl && cargo test

check: ## Run cargo check (Rust)
	cd rust_etl && cargo check

# Cleanup commands
clean: ## Remove all containers and volumes
	@echo "Removing all containers and volumes..."
	docker compose down -v
	docker system prune -f

clean-all: ## Remove everything including images
	@echo "Removing all containers, volumes, and images..."
	docker compose down -v --rmi all
	docker system prune -a -f

# Health check
health: ## Check health of all services
	@echo "Checking service health..."
	@docker compose ps
	@echo ""
	@echo "API Health Check:"
	@curl -s http://localhost:5000/api/v1/weather/health | python3 -m json.tool || echo "API not responding"

# Quick start for new developers
quickstart: setup build up ## Complete setup for new developers
	@echo ""
	@echo "🚀 Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your OpenWeatherMap API key"
	@echo "2. Run 'make logs' to see service logs"
	@echo "3. Visit http://localhost:5000/dashboard"
	@echo ""
	@echo "Useful commands:"
	@echo "  make logs          - View all logs"
	@echo "  make restart       - Restart services"
	@echo "  make health        - Check service health"
	@echo "  make clean         - Clean up containers"

# Docker utilities
docker-clean: ## Clean up unused Docker resources
	docker system prune -f
	docker volume prune -f

# Info commands
info: ## Show system information
	@echo "=== System Information ==="
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker compose version)"
	@echo "Rust version: $(shell cd rust_etl && cargo --version 2>/dev/null || echo 'Not installed')"
	@echo "Python version: $(shell python3 --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "=== Service Status ==="
	@docker compose ps

status: ## Show service status
	docker compose ps

