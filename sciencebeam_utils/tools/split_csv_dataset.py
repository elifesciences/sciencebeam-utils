import argparse
import logging
import errno
from math import trunc
from random import shuffle
from datetime import datetime
from itertools import chain
from typing import List

from backports import csv  # pylint: disable=no-name-in-module

from six import text_type

from sciencebeam_utils.beam_utils.io import open_file

from sciencebeam_utils.utils.csv import (
    csv_delimiter_by_filename,
    write_csv_rows
)

from sciencebeam_utils.utils.file_path import (
    strip_ext,
    get_ext
)

from sciencebeam_utils.tools.tool_utils import (
    setup_logging,
    add_default_args,
    process_default_args
)


LOGGER = logging.getLogger(__name__)


Row = List[str]


def extract_proportions_from_args(args):
    digits = 3
    proportions = [
        (name, round(p, digits))
        for name, p in [
            ('train', args.train),
            ('test', args.test),
            ('validation', args.validation)
        ]
        if p and p > 0
    ]
    if sum(p for _, p in proportions) > 1.0:
        raise ValueError('proportions add up to more than 1.0')
    if not args.test:
        proportions.append(('test', 1.0 - sum(p for _, p in proportions)))
    elif not args.validation:
        proportions.append(('validation', round(1.0 - sum(p for _, p in proportions), digits)))
    proportions = [(name, p) for name, p in proportions if p > 0]
    return proportions


def get_chunk_size_list(size, percentages, fill=False):
    chunk_size_list = [int(trunc(p * size)) for p in percentages]
    if fill:
        chunk_size_list[-1] = size - sum(chunk_size_list[:-1])
    return chunk_size_list


def split_row_chunks(rows, chunk_size_list):
    chunk_offset_list = [0]
    for chunk_size in chunk_size_list[0:-1]:
        chunk_offset_list.append(chunk_offset_list[-1] + chunk_size)
    LOGGER.debug('chunk_offset_list: %s', chunk_offset_list)
    LOGGER.debug('chunk_size_list: %s', chunk_size_list)
    return [
        rows[chunk_offset:chunk_offset + chunk_size]
        for chunk_offset, chunk_size in zip(chunk_offset_list, chunk_size_list)
    ]


def _to_hashable(value):
    return tuple(value)


def _to_row_set(rows):
    return {_to_hashable(row) for row in rows}


def _split_rows_without_existing_split(rows, percentages, fill=False):
    chunk_size_list = get_chunk_size_list(len(rows), percentages, fill=fill)
    return split_row_chunks(rows, chunk_size_list)


def _substract_list(list1, list2):
    return [a - b for a, b in zip(list1, list2)]


def split_rows(
        rows: List[Row],
        percentages: List[float],
        fill: bool = False,
        existing_split: List[List[Row]] = None) -> List[List[Row]]:
    if not existing_split:
        return _split_rows_without_existing_split(rows, percentages, fill=fill)
    LOGGER.debug('existing_split: %s', existing_split)
    all_current_rows = _to_row_set(rows)
    all_existing_rows = _to_row_set(chain(*existing_split))
    not_existing_rows = all_existing_rows - all_current_rows
    if not_existing_rows:
        LOGGER.warning(
            'some rows (%d of %d) from the existing split do not exist'
            ' in the source list and will be removed, e.g.: %s',
            len(not_existing_rows), len(all_existing_rows), list(not_existing_rows)[:3]
        )
        existing_split = [
            [row for row in existing_rows if _to_hashable(row) in all_current_rows]
            for existing_rows in existing_split
        ]
    remaining_rows = [row for row in rows if _to_hashable(row) not in all_existing_rows]
    chunk_size_list = get_chunk_size_list(len(rows), percentages, fill=fill)
    existing_chunk_size_list = [len(existing_rows) for existing_rows in existing_split]
    remaining_chunk_size_list = _substract_list(chunk_size_list, existing_chunk_size_list)
    return [
        existing_rows + new_split
        for existing_rows, new_split in zip(
            existing_split, split_row_chunks(remaining_rows, remaining_chunk_size_list)
        )
    ]


def output_filenames_for_names(names, prefix, ext):
    return [
        prefix + ('' if prefix.endswith('/') else '-') + name + ext
        for name in names
    ]


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', type=str, required=True,
        help='input csv/tsv file'
    )
    parser.add_argument(
        '--train', type=float, required=True,
        help='Train dataset proportion'
    )
    parser.add_argument(
        '--test', type=float, required=False,
        help='Test dataset proportion '
        '(if not specified it is assumed to be the remaining percentage)'
    )
    parser.add_argument(
        '--validation', type=float, required=False,
        help='Validation dataset proportion (requires test-proportion)'
    )
    parser.add_argument(
        '--random', action='store_true', default=False,
        help='randomise samples before doing the split'
    )
    parser.add_argument(
        '--fill', action='store_true', default=False,
        help='use up all of the remaining data rows for the last set'
    )
    parser.add_argument(
        '--no-extend-existing', action='store_true', default=False,
        help='do not extend and preserve the existing split (new entries will be addedby default)'
    )
    parser.add_argument(
        '--no-header', action='store_true', default=False,
        help='input file does not contain a header'
    )
    parser.add_argument(
        '--out', type=str, required=False,
        help='output csv/tsv file prefix or directory (if ending with slash)'
        ' will use input file name by default'
    )

    add_default_args(parser)

    return parser.parse_args(argv)


def process_args(args):
    if not args.out:
        args.out = strip_ext(args.input)


def read_csv_with_header(input_filename, delimiter, no_header):
    with open_file(input_filename, 'r') as f:
        reader = csv.reader(f, delimiter=text_type(delimiter))
        header_row = None if no_header else next(reader)
        data_rows = list(reader)
        return header_row, data_rows


def read_csv_data(input_filename, delimiter, no_header):
    _, data_rows = read_csv_with_header(input_filename, delimiter, no_header)
    return data_rows


def load_file_sets(filenames, delimiter, no_header):
    return [
        read_csv_data(filename, delimiter, no_header)
        for filename in filenames
    ]


def load_file_sets_or_none(filenames, delimiter, no_header):
    try:
        return load_file_sets(filenames, delimiter, no_header)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return None
        raise e


def save_file_set(output_filename, delimiter, header_row, set_data_rows):
    mime_type = 'text/tsv' if delimiter == '\t' else 'text/csv'
    with open_file(output_filename, 'w', mime_type=mime_type) as f:
        writer = csv.writer(f, delimiter=text_type(delimiter))
        if header_row:
            write_csv_rows(writer, [header_row])
        write_csv_rows(writer, set_data_rows)


def save_file_sets(output_filenames, delimiter, header_row, data_rows_by_set):
    for output_filename, set_data_rows in zip(output_filenames, data_rows_by_set):
        LOGGER.info('set size: %d (%s)', len(set_data_rows), output_filename)
        save_file_set(output_filename, delimiter, header_row, set_data_rows)


def get_backup_file_suffix():
    return '.backup-%s' % datetime.utcnow().strftime(r'%Y%m%d-%H%M%S')


def run(args):
    LOGGER.debug('args: %s', args)
    process_args(args)
    ext = get_ext(args.input)
    proportions = extract_proportions_from_args(args)
    output_filenames = output_filenames_for_names(
        [name for name, _ in proportions],
        args.out,
        ext
    )

    LOGGER.info('proportions: %s', proportions)
    LOGGER.info('output_filenames: %s', output_filenames)

    delimiter = csv_delimiter_by_filename(args.input)

    header_row, data_rows = read_csv_with_header(args.input, delimiter, args.no_header)
    LOGGER.info('number of rows: %d', len(data_rows))

    if args.random:
        shuffle(data_rows)

    existing_file_sets = load_file_sets_or_none(output_filenames, delimiter, args.no_header)

    data_rows_by_set = split_rows(
        data_rows,
        [p for _, p in proportions],
        fill=args.fill,
        existing_split=existing_file_sets if not args.no_extend_existing else None
    )

    if existing_file_sets:
        backup_suffix = get_backup_file_suffix()
        save_file_sets(
            [s + backup_suffix for s in output_filenames],
            delimiter,
            header_row,
            existing_file_sets
        )

    save_file_sets(
        output_filenames,
        delimiter,
        header_row,
        data_rows_by_set
    )


def main(argv=None):
    args = parse_args(argv)

    process_default_args(args)

    run(args)


if __name__ == '__main__':
    setup_logging()

    main()
