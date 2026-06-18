# Docker stack shortcuts.

COMPOSE        = docker compose -f docker/docker-compose.yml
COMPOSE_OLLAMA = docker compose -f docker/docker-compose.yml -f docker/docker-compose.bundled.yml

.PHONY: up up-ollama down logs build bench-scale bench-beir

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

bench-scale:      # synthetic vector-store scaling sweep -> var/scale/scale.png
	python scripts/benchmark_scale.py

bench-beir:       # BEIR retrieval-quality eval -> var/beir/beir_results.json (needs requirements-eval.txt)
	python scripts/benchmark_beir.py
