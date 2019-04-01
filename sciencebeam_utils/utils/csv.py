from __future__ import absolute_import

import os
import logging

from backports import csv  # pylint: disable=no-name-in-module


LOGGER = logging.getLogger(__name__)


TEMP_FILE_SUFFIX = '.part'


def csv_delimiter_by_filename(filename):
    if '.tsv' in filename:
        return '\t'
    return ','


def open_csv_output(filename):
    return open(filename, 'w')


def write_csv_rows(writer, iterable):
    writer.writerows(iterable)


def write_csv_row(writer, row):
    write_csv_rows(writer, [row])


def write_csv(filename, columns, iterable, delimiter=None):
    if delimiter is None:
        delimiter = csv_delimiter_by_filename(filename)
    is_stdout = filename in {'stdout', '/dev/stdout'}
    temp_filename = (
        filename + TEMP_FILE_SUFFIX
        if is_stdout
        else filename
    )
    if not is_stdout and os.path.isfile(filename):
        os.remove(filename)
    with open_csv_output(temp_filename) as csv_f:
        writer = csv.writer(csv_f, delimiter=delimiter)
        write_csv_rows(writer, [columns])
        write_csv_rows(writer, iterable)
    if not is_stdout:
        os.rename(temp_filename, filename)


def iter_dict_to_list(iterable, fields):
    return (
        [item.get(field) for field in fields]
        for item in iterable
    )


def write_dict_csv(filename, columns, iterable, delimiter=None):
    write_csv(filename, columns, iter_dict_to_list(iterable, columns), delimiter=delimiter)
