format:
	@poetry run python -Bm ruff main tests

format-check:
	@poetry run python -Bm ruff check -q main tests

test:
	@poetry run python -Bm coverage run -m pytest -rA tests

test-unit:
	@poetry run python -Bm coverage run -m pytest -rA tests/unit

test-integration:
	@poetry run python -Bm coverage run -m pytest -rA tests/integration

test-env:
	@tox -p

coverage-report:
	@poetry run python -Bm coverage report --show-missing

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

