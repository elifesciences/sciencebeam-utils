from collections import namedtuple

from .split_csv_dataset import (
    extract_proportions_from_args,
    split_rows,
    output_filenames_for_names,
    parse_args,
    run
)


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

    def test_should_add_new_files_to_existing_split_train_test(self):
        existing_split = [list(range(3)), list(range(3, 5))]
        assert split_rows(list(range(10)), [0.6, 0.4], existing_split=existing_split) == [
            existing_split[0] + list(range(5, 8)),
            existing_split[1] + list(range(8, 10))
        ]

    def test_should_add_new_files_to_existing_split_train_test_csv_row(self):
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

    def test_should_add_new_files_to_existing_uneven_split_train_test(self):
        existing_split = [list(range(3)), list(range(3, 4))]
        assert split_rows(list(range(10)), [0.6, 0.4], existing_split=existing_split) == [
            existing_split[0] + list(range(4, 7)),
            existing_split[1] + list(range(7, 10))
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

    def test_should_split_train_test_with_existing(self, tmpdir):
        file_list = tmpdir.join('file-list.tsv')
        train_file_list = tmpdir.join('file-list-train.tsv')
        test_file_list = tmpdir.join('file-list-test.tsv')
        file_list.write('\n'.join(['header', 'row1', 'row2', 'row3', 'row4']))
        train_file_list.write('\n'.join(['header', 'row1']))
        test_file_list.write('\n'.join(['header', 'row2']))

        args = parse_args([
            '--input', str(file_list),
            '--train', str(0.5),
            '--extend-existing'
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
