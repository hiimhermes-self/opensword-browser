.PHONY: run test lint

run:
	python -m opensword.browser

test:
	pytest tests/

lint:
	flake8 opensword/
