

.PHONY: lint test docs

lint:
	isort yamlsed tests
	black yamlsed tests
	flake8 yamlsed tests

test:
	poetry run pytest tests --cov=yamlsed --cov-report=term-missing

docs:
	poetry run mkdocs serve
