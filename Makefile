

.PHONY: lint test docs

lint:
	isort yamlsed tests
	black yamlsed tests
	flake8 yamlsed tests

test:
	poetry run pytest tests --cov=yamlsed --cov-report=term-missing

docs:
	printf '# Tests\n\n' > docs/tests.md
	poetry run pytest tests \
		--cov=yamlsed \
		--cov-report=term-missing \
		--cov-report=markdown:docs/coverage.md
	cat docs/coverage.md >> docs/tests.md
	poetry run mkdocs serve
