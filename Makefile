format:
	@poetry run python -Bm black main.py
requirements:
	@poetry export -o requirements.txt --without-hashes --without-urls
run-docker:
	@docker run --rm -p 8000:8000 myapi
build:
	docker build . -t myapi
