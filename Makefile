# Docker stack shortcuts.

COMPOSE        = docker compose -f docker/docker-compose.yml
COMPOSE_OLLAMA = docker compose -f docker/docker-compose.yml -f docker/docker-compose.bundled.yml

.PHONY: up up-ollama down logs build bench-scale bench-beir

# docker-compose references ../.env; create an empty one if missing so a fresh clone just works.
.env:
	touch .env

up: .env          # host Ollama
	$(COMPOSE) up

up-ollama: .env   # bundled Ollama (self-contained)
	$(COMPOSE_OLLAMA) up

down: .env        # stop all; keep volumes
	$(COMPOSE_OLLAMA) down

logs: .env
	$(COMPOSE) logs -f

build: .env
	$(COMPOSE) build

bench-scale:      # synthetic vector-store scaling sweep -> var/scale/scale.png
	python scripts/benchmark_scale.py

bench-beir:       # BEIR retrieval-quality eval -> var/beir/beir_results.json (needs requirements-eval.txt)
	python scripts/benchmark_beir.py
