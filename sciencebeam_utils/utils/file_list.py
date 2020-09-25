from __future__ import absolute_import

import os
import logging
from itertools import islice

from backports import csv  # pylint: disable=no-name-in-module

from six import text_type

from apache_beam.io.filesystems import FileSystems

from sciencebeam_utils.utils.csv import (
    csv_delimiter_by_filename
)

from sciencebeam_utils.beam_utils.io import open_file

from .file_path import (
    relative_path,
    join_if_relative_path
)


LOGGER = logging.getLogger(__name__)


def is_csv_or_tsv_file_list(file_list_path):
    return '.csv' in file_list_path or '.tsv' in file_list_path


def load_plain_file_list(file_list_path, limit=None):
    with open_file(file_list_path, 'r') as f:
        lines = (x.rstrip() for x in f)
        if limit:
            lines = islice(lines, 0, limit)
        return list(lines)


def load_csv_or_tsv_file_list(file_list_path, column, header=True, limit=None):
    delimiter = csv_delimiter_by_filename(file_list_path)
    with open_file(file_list_path, 'r') as f:
        reader = csv.reader(f, delimiter=text_type(delimiter))
        if not header:
            assert isinstance(column, int)
            column_index = column
        else:
            header_row = next(reader)
            if isinstance(column, int):
                column_index = column
            else:
                try:
                    column_index = header_row.index(column)
                except ValueError as exc:
                    raise ValueError(
                        'column %s not found, available columns: %s' %
                        (column, header_row)
                    ) from exc
        lines = (x[column_index] for x in reader)
        if limit:
            lines = islice(lines, 0, limit)
        return list(lines)


def to_absolute_file_list(base_path, file_list):
    return [join_if_relative_path(base_path, s) for s in file_list]


def to_relative_file_list(base_path, file_list):
    return [relative_path(base_path, s) for s in file_list]


def load_file_list(file_list_path, column, header=True, limit=None, to_absolute=True):
    if is_csv_or_tsv_file_list(file_list_path):
        file_list = load_csv_or_tsv_file_list(
            file_list_path, column=column, header=header, limit=limit
        )
    else:
        file_list = load_plain_file_list(file_list_path, limit=limit)
    if to_absolute:
        file_list = to_absolute_file_list(
            os.path.dirname(file_list_path), file_list
        )
    return file_list


def save_plain_file_list(file_list_path, file_list):
    with FileSystems.create(file_list_path) as f:
        f.write('\n'.join(file_list).encode('utf-8'))


def save_csv_or_tsv_file_list(file_list_path, file_list, column, header=True):
    if header:
        file_list = [column] + file_list
    save_plain_file_list(file_list_path, file_list)


def save_file_list(file_list_path, file_list, column, header=True):
    if is_csv_or_tsv_file_list(file_list_path):
        return save_csv_or_tsv_file_list(
            file_list_path, file_list, column=column, header=header
        )
    return save_plain_file_list(file_list_path, file_list)
