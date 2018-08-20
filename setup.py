from setuptools import find_packages, setup

import sciencebeam_utils


with open('requirements.txt', 'r') as f:
    REQUIRED_PACKAGES = f.readlines()

packages = find_packages()

setup(
    name='sciencebeam_utils',
    version=sciencebeam_utils.__version__,
    install_requires=REQUIRED_PACKAGES,
    packages=packages,
    include_package_data=True,
    description='ScienceBeam Utils',
)
