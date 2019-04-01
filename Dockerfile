FROM python:3.6.8-stretch

ENV PROJECT_HOME=/srv/sciencebeam-utils
WORKDIR ${PROJECT_HOME}

ENV VENV=${PROJECT_HOME}/venv
RUN pip install --no-cache-dir --only-binary --upgrade virtualenv \
    && virtualenv ${VENV}
ENV PYTHONUSERBASE=${VENV} PATH=${VENV}/bin:$PATH

COPY requirements.prereq.txt ${PROJECT_HOME}/
RUN pip install -r requirements.prereq.txt

COPY requirements.txt ${PROJECT_HOME}/
RUN pip install -r requirements.txt

COPY sciencebeam_utils ${PROJECT_HOME}/sciencebeam_utils
COPY *.conf *.sh *.in *.txt *.py .pylintrc .flake8 ${PROJECT_HOME}/

COPY requirements.dev.txt ${PROJECT_HOME}/
RUN pip install -r requirements.dev.txt

RUN python setup.py sdist bdist_wheel
