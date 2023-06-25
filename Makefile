format:
	@poetry run python -Bm black src/

format-check:
	@poetry run python -Bm black -q --check src/

test:
	@PYTHONPATH=src poetry run python -Bm coverage run -m pytest src/tests

test-unit:
	@PYTHONPATH=src poetry run python -Bm coverage run -m pytest src/tests/unit

test-integration:
	@PYTHONPATH=src poetry run python -Bm coverage run -m pytest src/tests/integration

coverage-report:
	@PYTHONPATH=src poetry run python -Bm coverage report

run:
	@PYTHONPATH=src poetry run python -Bm uvicorn src.main.entrypoint:api --port 8000 --reload

requirements:
	@poetry export -o requirements.txt

requirements-dev:
	@poetry export --only dev -o requirements-dev.txt

update-requirements:
	@poetry update

build: requirements requirements-dev
	@poetry run docker build -t myapi .

deploy: build
	@terraform apply -auto-approve -compact-warnings > /dev/null 2>&1

ping:
	@curl -f -LI http://127.0.0.1:8000 --silent --retry 10 --retry-max-time 3 --retry-all-errors >/dev/null 2>&1

