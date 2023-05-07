format:
	@poetry run python -Bm black src/
	@poetry run python -Bm isort src/

test:
	@PYTHONPATH=src poetry run python -Bm coverage run -m pytest src/tests

test-quiet:
	@PYTHONPATH=src poetry run python -Bm pytest --quiet src/tests >/dev/null 2>&1

run:
	@PYTHONPATH=src poetry run python -Bm uvicorn src.main.entrypoint:api --port 8000 --reload

requirements:
	@poetry export -o requirements.txt --without-hashes --without-urls

build: requirements
	@poetry run docker build . -t myapi

deploy: build
	@terraform apply -auto-approve -compact-warnings > /dev/null 2>&1

ping: deploy
	@curl -f -LI http://127.0.0.1:8000 --silent --retry 10 --retry-max-time 3 --retry-all-errors >/dev/null 2>&1

