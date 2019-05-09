from setuptools import find_packages, setup

import sciencebeam_utils


with open('requirements.txt', 'r') as f:
    REQUIRED_PACKAGES = f.readlines()


with open('README.md', 'r') as f:
    long_description = f.read()


packages = find_packages()


setup(
    name='sciencebeam_utils',
    version=sciencebeam_utils.__version__,
    author="eLife Sciences Publications, Ltd",
    url="https://github.com/elifesciences/sciencebeam-utils",
    install_requires=REQUIRED_PACKAGES,
    packages=packages,
    include_package_data=True,
    description='ScienceBeam Utils',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
