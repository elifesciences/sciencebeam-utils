#!/bin/sh

set -e

commit="$1"
repository="${2:-testpypi}"

if [ -z "$commit" ] || [ -z "$repository" ]; then
  echo "Usage: $0 <commit> [<repository>]"
  exit 1
fi

echo "commit=${commit}, repository=${repository}"

version=$($(dirname $0)/get-commit-version.sh 0.0.0.dev "${commit}")
echo 'test'
echo "version=${version}"

$(dirname $0)/set-version.sh "${version}"

cat sciencebeam_utils/__init__.py

python setup.py sdist bdist_wheel

twine upload --repository "${repository}" --verbose "dist/sciencebeam_utils-${version}"*
