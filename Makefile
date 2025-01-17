# ------------------ BACKEND ------------------
# Build & Run
.PHONY: dev
dev:
	make check-config
	make -j 2 watch up
	
.PHONY: watch
watch:
	@docker compose watch --no-up

.PHONY: up
up:
	@docker compose up --build

.PHONY: down
down:
	@docker compose down

.PHONY: attach
attach: 
	@docker attach cohere-toolkit-backend-1

.PHONY: logs
logs: 
	@@docker compose logs --follow --tail 100 $(service)

.PHONY: exec-backend
exec-backend:
	docker exec -ti cohere-toolkit-backend-1 bash 

.PHONY: exec-db
exec-db:
	docker exec -ti cohere-toolkit-db-1 bash

.PHONY: exec-terrarium
exec-terrarium:
	docker exec -ti -u root cohere-toolkit-terrarium-1 /bin/sh

# Testing & Linting
.PHONY: run-unit-tests
run-unit-tests:
	poetry run pytest -n auto src/backend/tests/unit/$(file) --cov=src/backend --cov-report=xml

.PHONY: run-unit-tests-debug
run-unit-tests-debug:
	poetry run pytest src/backend/tests/unit/$(file) --cov=src/backend --cov-report=xml

.PHONY: run-community-tests
run-community-tests:
	poetry run pytest -n auto src/community/tests/$(file) --cov=src/community --cov-report=xml

.PHONY: run-community-tests-debug
run-community-tests-debug:
	poetry run pytest src/community/tests/$(file) --cov=src/community --cov-report=xml

.PHONY: run-integration-tests
run-integration-tests:
	poetry run pytest -c src/backend/pytest_integration.ini src/backend/tests/integration/$(file)

.PHONY: test-db
test-db:
	docker compose stop test_db
	docker compose rm -f test_db
	docker compose up test_db -d

.PHONY: typecheck
typecheck:
	poetry run pyright

.PHONY: lint
lint:
	poetry run ruff check

.PHONY: lint-fix
lint-fix:
	poetry run ruff check --fix

# Database management
.PHONY: migration
migration:
	docker compose run --build backend alembic -c src/backend/alembic.ini revision --autogenerate -m "$(message)"

.PHONY: migrate
migrate:
	docker compose run --build backend alembic -c src/backend/alembic.ini upgrade head

.PHONY: downgrade
downgrade:
	docker compose run --build backend alembic -c src/backend/alembic.ini downgrade -1

.PHONY: reset-db
reset-db:
	docker compose down
	docker volume rm cohere_toolkit_db

# Setup 
.PHONY: install
install:
	poetry install --verbose --with dev

.PHONY: setup
setup:
	poetry install --with setup,dev --verbose
	poetry run python3 src/backend/scripts/cli/main.py

.PHONY: setup-use-community
setup-use-community:
	poetry install --with setup,community --verbose
	poetry run python3 src/backend/scripts/cli/main.py --use-community

.PHONY: win-setup
win-setup:
	poetry install --with setup --verbose
	poetry run python src/backend/scripts/cli/main.py

.PHONY: check-config-install
check-config-install:
	poetry install --with setup --verbose
	poetry run python src/backend/scripts/config/check_config.py

.PHONY: check-config 
check-config:
	poetry run python src/backend/scripts/config/check_config.py

.PHONY: first-run
first-run:
	make setup
	make migrate
	make dev

.PHONY: win-first-run
win-first-run:
	make win-setup
	make migrate
	make dev

# ------------------ FRONTEND ------------------
# Assistants Web
.PHONY: format-web
format-web:
	cd src/interfaces/assistants_web && npm run format:write

.PHONY: generate-client-web
generate-client-web:
	cd src/interfaces/assistants_web && npm run generate:client && npm run format:write

.PHONY: install-web
install-web:
	cd src/interfaces/assistants_web && npm install

.PHONY: build-web
build-web:
	cd src/interfaces/assistants_web && npm run build

# Coral Web
.PHONY: format-coral
format-coral:
	cd src/interfaces/coral_web && npm run format:write

.PHONY: generate-client-coral
generate-client-coral:
	cd src/interfaces/coral_web && npm run generate:client && npm run format:write

.PHONY: install-coral
install-coral:
	cd src/interfaces/coral_web && npm install

.PHONY: build-coral
build-coral:
	cd src/interfaces/coral_web && npm run build

# Debugging
.PHONY: vscode-debug
vscode-debug:
	@DEBUGGER_IDE=vscode docker compose -f docker-compose.debug.yml up --build

.PHONY: pycharm-debug
pycharm-debug:
	@DEBUGGER_IDE=pycharm docker compose -f docker-compose.debug.yml up --build
