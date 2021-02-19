import logging

import pytest


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logging.basicConfig(level='INFO')
    for name in ['tests', 'sciencebeam_utils']:
        logging.getLogger(name).setLevel('DEBUG')
