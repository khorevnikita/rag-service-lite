create_index:
	docker compose exec api python cli.py create-index --name my_rag_index

migration_create:
	docker compose exec api alembic revision -m"$(MSG)"

migrate:
	docker compose exec api alembic upgrade head

migrate_rollback:
	docker compose exec api alembic downgrade -1

model_seed:
	docker compose exec api python services/db/seeders/model_seeder.py

create_supertokens_db:
	docker compose up -d db
	@echo "Waiting for the database to be ready..."
	@until docker compose exec db pg_isready -U postgres > /dev/null 2>&1; do \
		sleep 1; \
		echo "Waiting..."; \
	done
	@echo "Database is ready."
	docker compose exec db psql -U postgres -c "CREATE DATABASE supertokens;"
	docker compose up -d

start:
	docker compose up -d

restart:
	docker compose restart

install: create_supertokens_db migrate model_seed create_index start restart

lint_api:
	cd api
	black ./ --exclude ".venv"
	isort ./ --skip ".venv"
	docformatter -i -r -e ".venv" --black --docstring-length 80 100 -- ./
	pylint ./ --ignore=.venv
	mypy ./ --exclude ".venv"
	find . -type f -name "*.py" -not -path "./.venv/*" | xargs radon cc -s -a
	bandit -r ./ --exclude ".venv"

lint_web:
	cd web
	npm run type-check
	npm run lint
	npm run format