RUN_PY2 = docker-compose run --rm sciencebeam-utils-py2
RUN_PY3 = docker-compose run --rm sciencebeam-utils-py3
PYTEST_ARGS =


dev-venv:
	rm -rf venv || true

	virtualenv -p python3.6 venv

	venv/bin/pip install -r requirements.txt

	venv/bin/pip install -r requirements.prereq.txt

	venv/bin/pip install -r requirements.dev.txt


build-all:
	docker-compose build --parallel


build-py2:
	docker-compose build sciencebeam-utils-py2


build-py3:
	docker-compose build sciencebeam-utils-py3


delete-pyc:
	find ./sciencebeam_utils/ -name '*.pyc' -delete


test-py2: build-py2 delete-pyc
	$(RUN_PY2) ./project_tests.sh


test-py3: build-py3 delete-pyc
	$(RUN_PY3) ./project_tests.sh


test: test-py2


watch-py2: build-py2 delete-pyc
	$(RUN_PY2) pytest-watch -- $(PYTEST_ARGS)


watch-py3: build-py3 delete-pyc
	$(RUN_PY3) pytest-watch -- $(PYTEST_ARGS)


watch: watch-py2
