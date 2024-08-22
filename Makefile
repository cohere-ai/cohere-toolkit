.PHONY: local-dev
local-dev:
	@docker compose up -d --build db redis
	make -j 2 local-dev-be local-dev-fe

.PHONY: local-dev-be
local-dev-be:
	poetry run uvicorn backend.main:app --reload
.PHONY: local-dev-fe
local-dev-fe:
	cd src/interfaces/assistants_web && npm run dev

.PHONY: local-migration
local-migration:
	poetry run alembic -c src/backend/alembic.ini revision --autogenerate -m ""

local-migrate:
	poetry run alembic -c src/backend/alembic.ini upgrade head


.PHONY: dev
dev:
	make -j 2 up

.PHONY: watch
watch:
	@docker compose watch --no-up

.PHONY: up
up:
	@docker compose up --build -d

.PHONY: down
down:
	@docker compose down

.PHONY: run-unit-tests
run-unit-tests:
	poetry run pytest src/backend/tests/unit --cov=src/backend --cov-report=xml

.PHONY: run-community-tests
run-community-tests:
	docker compose run --build backend poetry run pytest src/community/tests/$(file)

.PHONY: run-integration-tests
run-integration-tests:
	docker compose run --build backend poetry run pytest src/backend/tests/integration/$(file)

run-tests: run-unit-tests

.PHONY: attach
attach: 
	@docker attach cohere-toolkit-backend-1
logs: 
	@@docker-compose logs --follow --tail 100 $(service)

.PHONY: exec-backend
exec-backend:
	docker exec -ti cohere-toolkit-backend-1 bash 

.PHONY: exec-db
exec-db:
	docker exec -ti cohere-toolkit-db-1 bash

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

.PHONY: install
install:
	poetry install --verbose --with dev

.PHONY: setup
setup:
	poetry install --with setup,dev --verbose
	poetry run python3 src/backend/cli/main.py

.PHONY: setup-use-community
setup-use-community:
	poetry install --with setup,community --verbose
	poetry run python3 src/backend/cli/main.py --use-community

.PHONY: win-setup
win-setup:
	poetry install --with setup --verbose
	poetry run python src/backend/cli/main.py

.PHONY: lint
lint:
	poetry run ruff check

.PHONY: lint-fix
lint-fix:
	poetry run ruff check --fix

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

.PHONY: test-db
test-db:
	docker compose stop test_db
	docker compose rm -f test_db
	docker compose up test_db -d

.PHONY: dev-sync
dev-sync:
	@docker compose up --build sync_worker sync_publisher flower -d


.PHONY: dev-sync-down
dev-sync-down:
	@docker compose down sync_worker sync_publisher flower


.PHONY: typecheck
typecheck:
	poetry run pyright


carbon-webhook-server:
	poetry run fastapi dev  src/carbon_gmail_test/webhook_server.py


gmail-sandbox-app:
	python src/carbon_gmail_test/main.py  