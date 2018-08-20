# ScienceBeam Utils

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Provides utility functions to ScienceBeam projects.

## Pre-requisites

- Python 2.7 ([currently Apache Beam doesn't support Python 3](https://issues.apache.org/jira/browse/BEAM-1373))
- [Apache Beam](https://beam.apache.org/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

You can run the following to install Apache Beam:

```bash
pip install -r requirements.prereq.txt
```

## Dependencies

Dependencies not already mentioned in the prerequisites can be installed by running:

```bash
pip install -r requirements.txt
```

and:

```bash
pip install -r requirements.dev.txt
```

## Tests

Unit tests are written using [pytest](https://docs.pytest.org/). Run for example `pytest` or `pytest-watch`.

Some tests are marked with *slow*. You could exclude them when running the tests. For example:

```bash
pytest-watch -- -m "not slow"
```

## Docker

Build container and run project tests:

```bash
docker-compose build && \
    docker-compose run --rm sciencebeam-utils ./project_tests.sh && \
    echo "exit code: $?"
```
