dev:
	@docker compose watch
down:
	@docker compose down
run-tests:
	docker compose run --build backend poetry run pytest src/backend/tests/$(file)
run-community-tests:
	docker compose run --build backend poetry run pytest src/community/tests/$(file)
attach: 
	@docker attach cohere-toolkit-backend-1
exec-backend:
	docker exec -ti cohere-toolkit-backend-1 bash 
exec-db:
	docker exec -ti cohere-toolkit-db-1 bash
migration:
	docker compose run --build backend alembic -c src/backend/alembic.ini revision --autogenerate
migrate:
	docker compose run --build backend alembic -c src/backend/alembic.ini upgrade head
reset-db:
	docker compose down
	docker volume rm cohere_toolkit_db
setup:
	poetry install --with setup,community --verbose
	poetry run python3 src/backend/cli/main.py
win-setup:
	poetry install --with setup,community --verbose
	poetry run python src/backend/cli/main.py
lint:
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
