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

requirements:
	@poetry export -o requirements.txt

requirements-test:
	@poetry export --only test -o requirements-test.txt

update-requirements:
	@poetry update

build: requirements requirements-test
	@poetry run docker build -t myapi .

deploy: build
	@terraform apply -auto-approve -compact-warnings > /dev/null 2>&1

ping:
	@curl -f -LI http://127.0.0.1:8000 --silent --retry 10 --retry-max-time 3 --retry-all-errors >/dev/null 2>&1

