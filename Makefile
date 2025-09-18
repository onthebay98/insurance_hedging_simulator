.PHONY: install format lint test quickcheck

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

format:
	black src tests
	isort src tests

lint:
	mypy src

test:
	pytest

quickcheck:
	python -m pytest -q -k quickcheck -s
