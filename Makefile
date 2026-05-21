.PHONY: help up down stop start restart build rebuild pull ps logs life cdm end2end doctor \
	airflow init-db seed-neo fabric-up fabric-down

COMPOSE ?= docker compose
COMPOSE_FILE ?= docker-compose.yml
COMPOSE_FLAGS ?= -f $(COMPOSE_FILE)

help:
	@echo "Kloud Make Targets"
	@echo "  make up          - Start stack in detached mode"
	@echo "  make down        - Stop and remove stack"
	@echo "  make stop        - Stop stack without removing"
	@echo "  make start       - Start existing containers"
	@echo "  make restart     - Restart stack"
	@echo "  make build       - Build images"
	@echo "  make rebuild     - Rebuild images without cache"
	@echo "  make pull        - Pull latest images"
	@echo "  make ps          - Show container status"
	@echo "  make logs        - Follow compose logs"
	@echo "  make life        - Quick health/status checks"
	@echo "  make cdm         - Clean deploy mode (end-to-end)"
	@echo "  make end2end     - Alias for cdm"
	@echo "  make doctor      - Environment diagnostics"
	@echo "  make airflow     - List airflow DAGs"
	@echo "  make init-db     - Initialize postgres extensions"
	@echo "  make seed-neo    - Seed Neo4j ontology"
	@echo "  make fabric-up   - Start clx fabric compose"
	@echo "  make fabric-down - Stop clx fabric compose"

up:
	$(COMPOSE) $(COMPOSE_FLAGS) up -d

down:
	$(COMPOSE) $(COMPOSE_FLAGS) down

stop:
	$(COMPOSE) $(COMPOSE_FLAGS) stop

start:
	$(COMPOSE) $(COMPOSE_FLAGS) start

restart: down up

build:
	$(COMPOSE) $(COMPOSE_FLAGS) build

rebuild:
	$(COMPOSE) $(COMPOSE_FLAGS) build --no-cache

pull:
	$(COMPOSE) $(COMPOSE_FLAGS) pull

ps:
	$(COMPOSE) $(COMPOSE_FLAGS) ps

logs:
	$(COMPOSE) $(COMPOSE_FLAGS) logs -f --tail=200

life: ps
	@echo "[life] checking core health endpoints..."
	@if command -v curl >/dev/null 2>&1; then \
		curl -fsS http://localhost:8000/health >/dev/null && echo "[life] ok: http://localhost:8000/health" || echo "[life] warn: http://localhost:8000/health not ready"; \
		curl -fsS http://localhost:8000/status >/dev/null && echo "[life] ok: http://localhost:8000/status" || echo "[life] warn: http://localhost:8000/status not ready"; \
	else \
		echo "[life] curl not found; skipped http checks"; \
	fi

cdm:
	@echo "[cdm] clean deploy mode: down -> pull -> build -> up -> life"
	$(MAKE) down
	$(MAKE) pull
	$(MAKE) build
	$(MAKE) up
	$(MAKE) life

end2end: cdm

doctor:
	@echo "[doctor] checking toolchain..."
	@$(COMPOSE) version || true
	@docker --version || true
	@echo "[doctor] compose file: $(COMPOSE_FILE)"
	@$(COMPOSE) $(COMPOSE_FLAGS) config >/dev/null && echo "[doctor] compose config valid" || echo "[doctor] compose config has issues"

airflow:
	$(COMPOSE) $(COMPOSE_FLAGS) exec airflow airflow dags list

init-db:
	$(COMPOSE) $(COMPOSE_FLAGS) exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB -f /docker-entrypoint-initdb.d/01-timescale.sql

seed-neo:
	$(COMPOSE) $(COMPOSE_FLAGS) exec neo4j cypher-shell -u $$NEO4J_USER -p $$NEO4J_PASSWORD -f /opt/neo4j/import/ontologies.cypher

fabric-up:
	$(COMPOSE) -f docker-compose.clx.fabric.yml up -d

fabric-down:
	$(COMPOSE) -f docker-compose.clx.fabric.yml down
