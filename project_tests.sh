#!/bin/bash

set -e

docker run --rm elife/sciencebeam-utils /bin/bash -c \
    'pytest sciencebeam_utils && pylint sciencebeam_utils'
