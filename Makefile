.DEFAULT_GOAL := up

COMPOSE := docker compose -f docker-compose.yaml

rm-cache:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

stop:
	$(COMPOSE) down --remove-orphans

build: stop
	$(COMPOSE) build

debug: stop rm-cache
	$(COMPOSE) up

up: stop rm-cache
	$(COMPOSE) up -d

entry-%:
	$(COMPOSE) exec $* /bin/bash