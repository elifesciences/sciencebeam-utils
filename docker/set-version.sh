#!/bin/sh

set -e

version="$1"

sed -i -e "s/^__version__ = .*/__version__ = \"${version}\"/g" sciencebeam_utils/__init__.py
