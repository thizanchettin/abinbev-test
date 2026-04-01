COMPOSE_FILE = docker/airflow/docker-compose.yaml
PROJECT_NAME = abinbev-test

# Airflow

.PHONY: build
build: ## Build Airflow image
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) build

.PHONY: init
init: ## Initialize database and create admin user (first time only)
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) up airflow-init --wait

.PHONY: up
up: ## Start Airflow
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) up -d --wait

.PHONY: down
down: ## Stop Airflow
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) down

.PHONY: restart
restart: down up ## Restart Airflow

.PHONY: logs
logs: ## Follow logs from all services
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f

.PHONY: logs-scheduler
logs-scheduler: ## Follow scheduler logs
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f airflow-scheduler

.PHONY: logs-webserver
logs-webserver: ## Follow webserver logs
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f airflow-webserver

.PHONY: clean
clean: ## Remove all containers and volumes
	docker compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) down -v --remove-orphans

.PHONY: reset
reset: clean build init up ## Full reset: clean, build, init and start

# Helpers

.PHONY: help
help: ## List all available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
