.PHONY: run test lint

run:
	python -m opensword.browser

test:
	pytest tests/

lint:
	flake8 opensword/

install:
	pip install -r requirements.txt

run:
	python -m opensword.browser

test:
	pytest tests/ -v

lint:
	flake8 opensword/ || true

format:
	black opensword/ || true

clean:
	rm -rf build/ dist/ *.egg-info
