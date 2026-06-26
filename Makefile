.PHONY: help install test lint format clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies and pre-commit hooks
	pip install -r requirements.txt
	pip install pytest pre-commit
	pre-commit install

test:  ## Run unit tests
	python -m pytest test_ram_optimizer.py -v

lint:  ## Run ruff linter
	ruff check ram_optimizer.py test_ram_optimizer.py

format:  ## Run ruff formatter and fix lint issues
	ruff check --fix ram_optimizer.py test_ram_optimizer.py
	ruff format ram_optimizer.py test_ram_optimizer.py

check: lint test  ## Run lint and tests (CI target)

clean:  ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
