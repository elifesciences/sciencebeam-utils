DOCKER_COMPOSE_DEV = docker-compose
DOCKER_COMPOSE_CI = docker-compose -f docker-compose.yml -f docker-compose.ci.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)

VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

RUN = $(DOCKER_COMPOSE) run --rm sciencebeam-utils
PYTEST_ARGS =

COMMIT =
VERSION =
NO_BUILD =

venv-clean:
	@if [ -d "$(VENV)" ]; then \
		rm -rf "$(VENV)"; \
	fi


venv-create:
	python3 -m venv $(VENV)


dev-install:
	$(PIP) install -r requirements.build.txt
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements.prereq.txt
	$(PIP) install -r requirements.dev.txt


dev-venv: venv-create dev-install


dev-flake8:
	$(PYTHON) -m flake8 sciencebeam_utils tests setup.py


dev-pylint:
	$(PYTHON) -m pylint sciencebeam_utils tests setup.py


dev-lint: dev-flake8 dev-pylint


dev-pytest:
	$(PYTHON) -m pytest -p no:cacheprovider $(ARGS)


dev-watch:
	$(PYTHON) -m pytest_watch --verbose --ext=.py,.xsl -- -p no:cacheprovider -k 'not slow' $(ARGS)


dev-watch-slow:
	$(PYTHON) -m pytest_watch --verbose --ext=.py,.xsl -- -p no:cacheprovider $(ARGS)


dev-test: dev-lint dev-pytest


build:
	if [ "$(NO_BUILD)" != "y" ]; then \
		$(DOCKER_COMPOSE) build sciencebeam-utils; \
	fi


delete-pyc:
	find ./sciencebeam_utils/ -name '*.pyc' -delete


test: build
	$(RUN) ./project_tests.sh


watch: build delete-pyc
	$(RUN) pytest-watch -- $(PYTEST_ARGS)


ci-build:
	make DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" build


ci-test:
	make DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" test


ci-push-testpypi:
	$(DOCKER_COMPOSE_CI) run --rm \
		-v $$PWD/.pypirc:/root/.pypirc \
		sciencebeam-utils \
		./docker/push-testpypi-commit-version.sh "$(COMMIT)"


ci-push-pypi:
	$(DOCKER_COMPOSE_CI) run --rm \
		-v $$PWD/.pypirc:/root/.pypirc \
		sciencebeam-utils \
		./docker/push-pypi-version.sh "$(VERSION)"
