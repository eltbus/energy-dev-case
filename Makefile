format:
	@poetry run python -Bm black main.py
requirements:
	@poetry export -o requirements.txt --without-hashes --without-urls
run-local:
	@poetry run python -Bm uvicorn main:app --host 0.0.0.0
run-docker:
	@docker run --rm -p 8000:8000 myapi
build:
	@poetry run docker build . -t myapi
