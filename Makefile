# Docker stack shortcuts.

COMPOSE        = docker compose
COMPOSE_OLLAMA = docker compose -f docker-compose.yml -f docker-compose.bundled.yml

.PHONY: up up-ollama down logs build

up:               # host Ollama
	$(COMPOSE) up

up-ollama:        # bundled Ollama (self-contained)
	$(COMPOSE_OLLAMA) up

down:             # stop all; keep volumes
	$(COMPOSE_OLLAMA) down

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build
