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
run-agent-router-tests:
	docker compose run --build backend poetry run pytest src/backend/tests/routers/test_agent.py
run-user-router-tests:
	docker compose run --build backend poetry run pytest src/backend/tests/routers/test_user.py
run-community-tests:
	docker compose run --build backend poetry run pytest src/community/tests/$(file)
attach: 
	@docker compose logs -f backend
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
	poetry install --with setup --verbose
	poetry run python3 src/backend/cli/main.py
setup-use-community:
	poetry install --with setup,community --verbose
	poetry run python3 src/backend/cli/main.py --use-community
win-setup:
	poetry install --with setup --verbose
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