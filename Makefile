.PHONY: help format test clean

help:
	@echo "Available targets:"
	@echo "  format        - Fix code formatting with black"
	@echo "  test          - Run pytest tests"
	@echo "  clean         - Remove Python cache files"

format:
	black src/ rules/ tests/

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
