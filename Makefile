

lint:
	isort yamly tests
	black yamly tests
	flake8 yamly tests

test:
	poetry run pytest tests --cov=yamly --cov-report=term-missing
