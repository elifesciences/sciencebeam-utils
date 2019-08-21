import subprocess
from mock import patch

import pytest

from six import text_type, binary_type

from sciencebeam_utils.beam_utils.main import get_cloud_project


PROJECT_1 = 'project1'


@pytest.fixture(name='check_output_mock')
def _check_output_mock():
    with patch.object(subprocess, 'check_output') as mock:
        yield mock


class TestGetCloudProject(object):
    def test_should_return_project(self, check_output_mock):
        check_output_mock.return_value = PROJECT_1
        assert get_cloud_project() == PROJECT_1

    def test_should_return_text_type_if_check_output_returns_bytes(self, check_output_mock):
        check_output_mock.return_value = binary_type(PROJECT_1)
        assert isinstance(get_cloud_project(), text_type)

    def test_should_return_text_type_if_check_output_text_type(self, check_output_mock):
        check_output_mock.return_value = text_type(PROJECT_1)
        assert isinstance(get_cloud_project(), text_type)
