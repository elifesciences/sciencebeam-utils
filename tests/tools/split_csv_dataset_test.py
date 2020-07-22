from collections import namedtuple
from datetime import datetime

from mock import patch

import pytest

from sciencebeam_utils.tools import split_csv_dataset as split_csv_dataset_module
from sciencebeam_utils.tools.split_csv_dataset import (
    extract_proportions_from_args,
    split_rows,
    output_filenames_for_names,
    get_backup_file_suffix,
    parse_args,
    run
)


@pytest.fixture(name='get_backup_file_suffix_mock')
def _get_backup_file_suffix():
    with patch.object(split_csv_dataset_module, 'get_backup_file_suffix') as m:
        yield m


def create_args(**kwargs):
    return namedtuple('args', kwargs.keys())(**kwargs)


class TestExtractProportionsFromArgs:
    def test_should_create_train_test_split_with_only_train_specified(self):
        assert extract_proportions_from_args(
            create_args(train=0.6, test=None, validation=None)
        ) == [('train', 0.6), ('test', 0.4)]

    def test_should_create_train_test_validation_split_with_train_and_test_specified(self):
        assert extract_proportions_from_args(
            create_args(train=0.6, test=0.3, validation=None)
        ) == [('train', 0.6), ('test', 0.3), ('validation', 0.1)]

    def test_should_not_add_validation_if_remaining_percentage_is_zero(self):
        assert extract_proportions_from_args(
            create_args(train=0.6, test=0.4, validation=None)
        ) == [('train', 0.6), ('test', 0.4)]


def _chars_to_rows(chars):
    return [[c] for c in chars]


def _chars_to_rows_list(*chars_list):
    return [_chars_to_rows(chars) for chars in chars_list]


class TestSplitRows:
    def test_should_split_train_test(self):
        assert split_rows(
            _chars_to_rows('0123456789'), [0.6, 0.4]
        ) == _chars_to_rows_list('012345', '6789')

    def test_should_split_train_test_validation(self):
        assert split_rows(
            _chars_to_rows('0123456789'), [0.6, 0.3, 0.1]
        ) == _chars_to_rows_list('012345', '678', '9')

    def test_should_round_down(self):
        assert split_rows(
            _chars_to_rows('0123456789X'), [0.6, 0.4]
        ) == _chars_to_rows_list('012345', '6789')

    def test_should_fill_last_chunk_if_enabled(self):
        assert split_rows(
            _chars_to_rows('0123456789X'), [0.6, 0.4], fill=True
        ) == _chars_to_rows_list('012345', '6789X')

    def test_should_add_new_items_to_existing_split_train_test(self):
        existing_split = _chars_to_rows_list('012', '34')
        assert split_rows(
            _chars_to_rows('0123456789'), [0.6, 0.4], existing_split=existing_split
        ) == _chars_to_rows_list('012' + '567', '34' + '89')

    def test_should_add_new_items_to_existing_uneven_split_train_test(self):
        existing_split = _chars_to_rows_list('012', '3')
        assert split_rows(
            _chars_to_rows('0123456789'), [0.6, 0.4], existing_split=existing_split
        ) == _chars_to_rows_list('012' + '456', '3' + '789')

    def test_should_remove_items_not_present_in_total_list(self):
        existing_split = _chars_to_rows_list('1x', '2y')
        assert split_rows(
            _chars_to_rows('1234'), [0.5, 0.5], existing_split=existing_split
        ) == _chars_to_rows_list('13', '24')


class TestGetOutputFilenamesForNames:
    def test_should_add_name_and_ext_with_path_sep_if_out_ends_with_slash(self):
        assert output_filenames_for_names(
            ['train', 'test'], 'out/', '.tsv'
        ) == ['out/train.tsv', 'out/test.tsv']

    def test_should_add_name_and_ext_with_hyphen_if_out_does_not_end_with_slash(self):
        assert output_filenames_for_names(
            ['train', 'test'], 'out', '.tsv'
        ) == ['out-train.tsv', 'out-test.tsv']


class TestGetBackupFileSuffix:
    @patch.object(split_csv_dataset_module, 'datetime')
    def test_should_return_backup_suffix_with_datetime(self, datetime_mock):
        datetime_mock.utcnow.return_value = datetime(2001, 2, 3, 4, 5, 6)
        assert get_backup_file_suffix() == '.backup-20010203-040506'


class TestRun:
    def test_should_split_train_test(self, tmpdir):
        file_list = tmpdir.join('file-list.tsv')
        train_file_list = tmpdir.join('file-list-train.tsv')
        test_file_list = tmpdir.join('file-list-test.tsv')
        file_list.write('\n'.join(['header', 'row1', 'row2', 'row3', 'row4']))

        args = parse_args([
            '--input', str(file_list),
            '--train', str(0.5)
        ])
        run(args)

        assert (
            train_file_list.read().splitlines() ==
            ['header', 'row1', 'row2']
        )

        assert (
            test_file_list.read().splitlines() ==
            ['header', 'row3', 'row4']
        )

    def test_should_split_train_test_with_existing_split(self, tmpdir):
        file_list = tmpdir.join('file-list.tsv')
        train_file_list = tmpdir.join('file-list-train.tsv')
        test_file_list = tmpdir.join('file-list-test.tsv')
        file_list.write('\n'.join(['header', 'row1', 'row2', 'row3', 'row4']))
        train_file_list.write('\n'.join(['header', 'row1']))
        test_file_list.write('\n'.join(['header', 'row2']))

        args = parse_args([
            '--input', str(file_list),
            '--train', str(0.5)
        ])
        run(args)

        assert (
            train_file_list.read().splitlines() ==
            ['header', 'row1', 'row3']
        )

        assert (
            test_file_list.read().splitlines() ==
            ['header', 'row2', 'row4']
        )

    def test_should_backup_existing_split(self, tmpdir, get_backup_file_suffix_mock):
        get_backup_file_suffix_mock.return_value = '.backup'
        file_list = tmpdir.join('file-list.tsv')
        train_file_list = tmpdir.join('file-list-train.tsv')
        test_file_list = tmpdir.join('file-list-test.tsv')
        file_list.write('\n'.join(['header', 'row1', 'row2', 'row3', 'row4']))
        train_file_list.write('\n'.join(['header', 'row1']))
        test_file_list.write('\n'.join(['header', 'row2']))

        args = parse_args([
            '--input', str(file_list),
            '--train', str(0.5)
        ])
        run(args)

        assert (
            tmpdir.join('file-list-train.tsv.backup').read().splitlines() ==
            ['header', 'row1']
        )

        assert (
            tmpdir.join('file-list-test.tsv.backup').read().splitlines() ==
            ['header', 'row2']
        )
