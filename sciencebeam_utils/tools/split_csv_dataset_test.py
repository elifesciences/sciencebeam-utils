from collections import namedtuple
from datetime import datetime

from mock import patch

import pytest

from . import split_csv_dataset as split_csv_dataset_module
from .split_csv_dataset import (
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


class TestExtractProportionsFromArgs(object):
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


def _flat_rows_to_nested_rows(rows):
    return [[row] for row in rows]


def _flat_rows_list_to_nested_rows_list(rows_list):
    return [_flat_rows_to_nested_rows(rows) for rows in rows_list]


class TestSplitRows(object):
    def test_should_split_train_test(self):
        assert split_rows(list(range(10)), [0.6, 0.4]) == [
            list(range(6)),
            list(range(6, 10))
        ]

    def test_should_split_train_test_validation(self):
        assert split_rows(list(range(10)), [0.6, 0.3, 0.1]) == [
            list(range(6)),
            list(range(6, 9)),
            list(range(9, 10))
        ]

    def test_should_round_down(self):
        assert split_rows(list(range(11)), [0.6, 0.4]) == [
            list(range(6)),
            list(range(6, 10))
        ]

    def test_should_fill_last_chunk_if_enabled(self):
        assert split_rows(list(range(11)), [0.6, 0.4], fill=True) == [
            list(range(6)),
            list(range(6, 11))
        ]

    def test_should_add_new_items_to_existing_split_train_test(self):
        existing_split = [list(range(3)), list(range(3, 5))]
        assert split_rows(list(range(10)), [0.6, 0.4], existing_split=existing_split) == [
            existing_split[0] + list(range(5, 8)),
            existing_split[1] + list(range(8, 10))
        ]

    def test_should_add_new_items_to_existing_split_train_as_test_nested_rows(self):
        existing_split = [list(range(3)), list(range(3, 5))]
        assert split_rows(
            _flat_rows_to_nested_rows(range(10)), [0.6, 0.4],
            existing_split=_flat_rows_list_to_nested_rows_list(
                existing_split
            )
        ) == _flat_rows_list_to_nested_rows_list([
            existing_split[0] + list(range(5, 8)),
            existing_split[1] + list(range(8, 10))
        ])

    def test_should_add_new_items_to_existing_uneven_split_train_test(self):
        existing_split = [list(range(3)), list(range(3, 4))]
        assert split_rows(list(range(10)), [0.6, 0.4], existing_split=existing_split) == [
            existing_split[0] + list(range(4, 7)),
            existing_split[1] + list(range(7, 10))
        ]

    def test_should_remove_items_not_present_in_total_list(self):
        existing_split = [['1', 'x'], ['2', 'y']]
        assert split_rows(['1', '2', '3', '4'], [0.5, 0.5], existing_split=existing_split) == [
            ['1', '3'],
            ['2', '4']
        ]


class TestGetOutputFilenamesForNames(object):
    def test_should_add_name_and_ext_with_path_sep_if_out_ends_with_slash(self):
        assert output_filenames_for_names(
            ['train', 'test'], 'out/', '.tsv'
        ) == ['out/train.tsv', 'out/test.tsv']

    def test_should_add_name_and_ext_with_hyphen_if_out_does_not_end_with_slash(self):
        assert output_filenames_for_names(
            ['train', 'test'], 'out', '.tsv'
        ) == ['out-train.tsv', 'out-test.tsv']


class TestGetBackupFileSuffix(object):
    @patch.object(split_csv_dataset_module, 'datetime')
    def test_should_return_backup_suffix_with_datetime(self, datetime_mock):
        datetime_mock.utcnow.return_value = datetime(2001, 2, 3, 4, 5, 6)
        assert get_backup_file_suffix() == '.backup-20010203-040506'


class TestRun(object):
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
