.PHONY: help format format-check lint test clean install

help:
	@echo "Available targets:"
	@echo "  format        - Fix code formatting with black"
	@echo "  format-check  - Check code formatting without modifying files"
	@echo "  lint          - Run flake8 linter"
	@echo "  test          - Run pytest tests"
	@echo "  clean         - Remove Python cache files"
	@echo "  install       - Install package in development mode"

format:
	black src/ rules/ tests/

format-check:
	black --check src/ rules/ tests/

lint:
	flake8 src/ rules/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ rules/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

test:
	pytest tests/ -v --cov=src --cov=rules --cov-report=xml --cov-report=term

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov

install:
	pip install -e .
