.PHONY: help venv install install-dev test lint format clean run-example hooks

help:
	@echo "Available targets:"
	@echo "  venv         - Create virtual environment with uv"
	@echo "  install      - Install package with uv"
	@echo "  install-dev  - Install with dev dependencies"
	@echo "  hooks        - Install pre-commit hooks"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  clean        - Remove build artifacts"
	@echo "  run-example  - Run example workflow"

venv:
	uv venv --python 3.10

install: venv
	uv pip install -e .

install-dev: venv
	uv pip install -e ".[dev]"

hooks:
	uv run pre-commit install

test:
	uv run pytest -v --cov=forge --cov-report=html --cov-report=term

lint:
	uv run ruff check forge/
	uv run black --check forge/

format:
	uv run ruff check --fix forge/
	uv run black forge/

clean:
	rm -rf build/ dist/ *.egg-info .venv/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/

run-example:
	@echo "==> Initializing example workshop..."
	uv run workshopforge init examples/test-run
	@echo "\n==> Validating specs..."
	uv run workshopforge validate --spec-dir examples/test-run/spec
	@echo "\n==> Generating instructor materials..."
	uv run workshopforge generate --spec-dir examples/test-run/spec --target examples/test-run/out/instructor
	@echo "\n==> Running compliance check..."
	uv run workshopforge ai check --spec-dir examples/test-run/spec
	@echo "\n==> Done! Check examples/test-run/out/"
