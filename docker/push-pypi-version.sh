#!/bin/sh

set -e

version="$1"
repository="${2:-pypi}"

if [ -z "$version" ] || [ -z "$repository" ]; then
  echo "Usage: $0 <version> [<repository>]"
  exit 1
fi

echo "version=${version}, repository=${repository}"

cat sciencebeam_utils/__init__.py

twine upload --repository "${repository}" --verbose "dist/sciencebeam_utils-${version}"*
