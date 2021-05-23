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

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr .pytest_cache

clean-docker: ## prune unused images
	docker image prune -af

lint: ## check style with flake8
	# stop the build if there are Python syntax errors or undefined names
	poetry run flake8 phoney tests --count --select=E9,F63,F7,F82 --show-source --statistics --builtins="_"
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	poetry run flake8 phoney tests --count --ignore=E203,E722,W503,E401,C901 --exit-zero --max-complexity=10 --max-line-length=127 --statistics --builtins="_"

format: ## auto format all the code with black
	poetry run black ./phoney --line-length 127

run:
	poetry run uvicorn phoney.app.main:app --reload

server:
	poetry run uvicorn phoney.app.main:app --env-file .env

test: ## run tests quickly with the default Python
	poetry run pytest

test-debug: ## run tests with debugging enabled
	LOGLEVEL=debug; poetry run py.test -s --pdb

test-coverage: ## check code coverage quickly with the default Python
	poetry run coverage run --source phoney -m pytest
	poetry run coverage report -m

test-coverage-report: test-coverage ## Report coverage to Coveralls
	poetry run coveralls

requirements:
	poetry update
	poetry export -f requirements.txt --output requirements.txt

build: clean test requirements
	poetry build

build-image: clean-docker test requirements
	docker build . -t phoney:latest

tag:
	@export VERSION_TAG=`python3 -c "from phoney import __version__; print(__version__)"` \
	&& git tag v$$VERSION_TAG

push-tag: tag
	@export VERSION_TAG=`python3 -c "from phoney import __version__; print(__version__)"` \
	&& git push origin v$$VERSION_TAG

release: test build push-tag
	poetry publish
