#!/bin/bash

set -e

# avoid issues with .pyc/pyo files when mounting source directory
export PYTHONOPTIMIZE=

echo "running flake8"
flake8 sciencebeam_utils tests

echo "running pylint"
PYLINTHOME=/tmp/sciencebeam-utils \
  pylint sciencebeam_utils tests

echo "running tests"
pytest -p no:cacheprovider

echo "done"
