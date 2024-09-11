run:
	python3 main.py

install:
	pip3 install -r requirements.txt

run_surrealdb:
	docker run --rm --pull always -p 8000:8000 surrealdb/surrealdb:latest star
