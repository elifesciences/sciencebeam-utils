from setuptools import find_packages, setup


with open('requirements.txt', 'r') as f:
    REQUIRED_PACKAGES = f.readlines()

packages = find_packages()

setup(
    name='sciencebeam_utils',
    version='0.0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=packages,
    include_package_data=True,
    description='ScienceBeam Utils',
)
