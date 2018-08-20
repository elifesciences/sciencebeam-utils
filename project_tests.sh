#!/bin/bash

set -e

pytest sciencebeam_utils && \
    pylint sciencebeam_utils
