format:
	@poetry run python -Bm black src/
	@poetry run python -Bm isort src/

test:
	@PYTHONPATH=src poetry run python -Bm coverage run -m pytest src/tests -vv 

run:
	@PYTHONPATH=src poetry run python -Bm uvicorn src.main.entrypoint:api --port 8000 --reload

requirements:
	@poetry export -o requirements.txt --without-hashes --without-urls

build:
	@poetry run docker build . -t myapi
