import argparse
import subprocess
from mock import patch

import pytest

from six import text_type

from sciencebeam_utils.utils.collection import extend_dict

import sciencebeam_utils.beam_utils.main as main_module
from sciencebeam_utils.beam_utils.main import (
    get_cloud_project,
    process_cloud_args,
    add_cloud_args
)


PROJECT_1 = 'project1'


DEFAULT_ARGS = dict(
    project=None,
    job_name=None,
    job_name_suffix=None,
    num_workers=10,
    cloud=False
)

DEFAULT_OUTPUT_PATH = '/tmp/output'


@pytest.fixture(name='check_output_mock')
def _check_output_mock():
    with patch.object(subprocess, 'check_output') as mock:
        yield mock


@pytest.fixture(name='get_cloud_project_mock')
def _get_cloud_project_mock():
    with patch.object(main_module, 'get_cloud_project') as mock:
        yield mock


class TestGetCloudProject:
    def test_should_return_project(self, check_output_mock):
        check_output_mock.return_value = PROJECT_1
        assert get_cloud_project() == PROJECT_1

    def test_should_return_text_type_if_check_output_returns_bytes(self, check_output_mock):
        check_output_mock.return_value = PROJECT_1.encode('utf-8')
        assert isinstance(get_cloud_project(), text_type)

    def test_should_return_text_type_if_check_output_text_type(self, check_output_mock):
        check_output_mock.return_value = text_type(PROJECT_1)
        assert isinstance(get_cloud_project(), text_type)


class TestAddCloudArgs:
    def test_should_accept_num_workers_with_underscore(self):
        args = add_cloud_args(argparse.ArgumentParser()).parse_args(['--num_workers=123'])
        assert args.num_workers == 123

    def test_should_accept_num_workers_with_hyphen(self):
        args = add_cloud_args(argparse.ArgumentParser()).parse_args(['--num-workers=123'])
        assert args.num_workers == 123

    def test_should_accept_max_workers(self):
        args = add_cloud_args(argparse.ArgumentParser()).parse_args(['--max-workers=123'])
        assert args.max_num_workers == 123

    def test_should_accept_job_name_with_underscore(self):
        args = add_cloud_args(argparse.ArgumentParser()).parse_args(['--job_name=job1'])
        assert args.job_name == 'job1'

    def test_should_accept_job_name_with_hyphen(self):
        args = add_cloud_args(argparse.ArgumentParser()).parse_args(['--job-name=job1'])
        assert args.job_name == 'job1'


@pytest.mark.usefixtures('get_cloud_project_mock')
class TestProcessCloudArgs:
    def test_should_use_get_cloud_project_if_project_is_empty(
            self, get_cloud_project_mock):
        get_cloud_project_mock.return_value = PROJECT_1
        args = argparse.Namespace(**extend_dict(DEFAULT_ARGS, {
            'cloud': True,
            'project': None
        }))
        process_cloud_args(args, output_path=DEFAULT_OUTPUT_PATH)
        assert args.project == PROJECT_1  # pylint: disable=no-member

    def test_should_not_call_get_cloud_project_if_cloud_is_false(
            self, get_cloud_project_mock):
        args = argparse.Namespace(**extend_dict(DEFAULT_ARGS, {
            'cloud': False
        }))
        process_cloud_args(args, output_path=DEFAULT_OUTPUT_PATH)
        get_cloud_project_mock.assert_not_called()

    def test_should_not_call_get_cloud_project_if_project_was_specified(
            self, get_cloud_project_mock):
        args = argparse.Namespace(**extend_dict(DEFAULT_ARGS, {
            'cloud': True,
            'project': PROJECT_1
        }))
        process_cloud_args(args, output_path=DEFAULT_OUTPUT_PATH)
        get_cloud_project_mock.assert_not_called()
