dev:
	make -j 2 watch up
watch:
	@docker compose watch --no-up
up:
	@docker compose up --build
down:
	@docker compose down
run-tests:
	docker compose run --build backend poetry run pytest src/backend/tests/$(file)
run-community-tests:
	docker compose run --build backend poetry run pytest src/community/tests/$(file)
attach: 
	@docker attach cohere-toolkit-backend-1
logs: 
	@docker compose logs -f backend
exec-backend:
	docker exec -ti cohere-toolkit-backend-1 bash 
exec-db:
	docker exec -ti cohere-toolkit-db-1 bash
migration:
	docker compose run --build backend alembic -c src/backend/alembic.ini revision --autogenerate
migrate:
	docker compose run --build backend alembic -c src/backend/alembic.ini upgrade head
downgrade:
	docker compose run --build backend alembic -c src/backend/alembic.ini downgrade -1
reset-db:
	docker compose down
	docker volume rm cohere_toolkit_db
setup:
	poetry install --with setup --verbose
	poetry run python3 src/backend/cli/main.py
setup-use-community:
	poetry install --with setup,community --verbose
	poetry run python3 src/backend/cli/main.py --use-community
win-setup:
	poetry install --with setup --verbose
	poetry run python src/backend/cli/main.py
lint:
	poetry run autoflake --in-place --recursive --ignore-init-module-imports .
	poetry run black .
	poetry run isort .
first-run:
	make setup
	make migrate
	make dev
win-first-run:
	make win-setup
	make migrate
	make dev
format-web:
	cd src/interfaces/coral_web && npm run format:write
generate-client-web:
	cd src/interfaces/coral_web && npm run generate:client && npm run format:write
install-web:
	cd src/interfaces/coral_web && npm install
build-web:
	cd src/interfaces/coral_web && npm run build
