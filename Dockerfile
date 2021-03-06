ARG base_image
FROM ${base_image}

ENV PROJECT_HOME=/srv/sciencebeam-utils
WORKDIR ${PROJECT_HOME}

ENV VENV=${PROJECT_HOME}/venv
RUN python3 -m venv ${VENV}
ENV PYTHONUSERBASE=${VENV} PATH=${VENV}/bin:$PATH

COPY requirements.build.txt ${PROJECT_HOME}/
RUN pip install -r requirements.build.txt

COPY requirements.prereq.txt ${PROJECT_HOME}/
RUN pip install -r requirements.prereq.txt

COPY requirements.txt ${PROJECT_HOME}/
RUN pip install -r requirements.txt

COPY requirements.dev.txt ${PROJECT_HOME}/
RUN pip install -r requirements.dev.txt

COPY sciencebeam_utils ${PROJECT_HOME}/sciencebeam_utils
COPY tests ${PROJECT_HOME}/tests
COPY README.md *.conf *.sh *.in *.txt *.py .pylintrc .flake8 pytest.ini ${PROJECT_HOME}/

ARG version
ADD docker ./docker
RUN ls -l && ./docker/set-version.sh "${version}"
LABEL org.opencontainers.image.version=${version}

RUN python setup.py sdist bdist_wheel
