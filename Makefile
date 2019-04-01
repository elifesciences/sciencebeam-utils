RUN = docker-compose run --rm sciencebeam-utils
PYTEST_ARGS =


dev-venv:
	rm -rf venv || true

	virtualenv -p python3.6 venv

	venv/bin/pip install -r requirements.txt

	venv/bin/pip install -r requirements.prereq.txt

	venv/bin/pip install -r requirements.dev.txt


build:
	docker-compose build


test: build
	$(RUN) ./project_tests.sh -- $(PYTEST_ARGS)


watch: build
	$(RUN) pytest-watch -- $(PYTEST_ARGS)
