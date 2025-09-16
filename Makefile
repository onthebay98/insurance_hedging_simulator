.PHONY: install format lint test quickcheck

install:
\tpython -m pip install --upgrade pip
\tpip install -r requirements.txt

format:
\tblack src tests
\tisort src tests

lint:
\tmypy src

test:
\tpytest

quickcheck:
\tpython -m pytest -q -k quickcheck -s
