.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr .pytest_cache

clean-docker:
	docker image prune -af

lint:
	poetry run flake8 phoney tests --count --select=E9,F63,F7,F82 --show-source --statistics --builtins="_"
	poetry run flake8 phoney tests --count --ignore=E203,E722,W503,E401,C901 --exit-zero --max-complexity=10 --max-line-length=127 --statistics --builtins="_"

format:
	poetry run black ./phoney --line-length 127

serve:
	poetry run uvicorn phoney.app.main:app --env-file .env

test:
	poetry run pytest

test-debug:
	LOGLEVEL=debug; poetry run py.test -s --pdb

test-coverage:
	poetry run coverage run --source phoney -m pytest
	poetry run coverage report -m

test-coverage-report: test-coverage
	poetry run coveralls

requirements:
	poetry update
	poetry export -f requirements.txt --output requirements.txt

build: clean test requirements
	poetry build

build-image: clean-docker test requirements
	docker build . -t phoney:latest

build-all: build build-image

tag:
	@export VERSION_TAG=`python3 -c "from phoney import __version__; print(__version__)"` \
	&& git tag v$$VERSION_TAG \
	&& git push origin v$$VERSION_TAG

release: test build push-tag
	poetry publish
