from __future__ import absolute_import

import logging
from io import StringIO

from backports import csv  # pylint: disable=no-name-in-module

from six import text_type

import apache_beam as beam
from apache_beam.io.textio import WriteToText
from apache_beam.io.filesystem import CompressionTypes
from apache_beam.io.filebasedsource import FileBasedSource

from sciencebeam_utils.beam_utils.utils import (
    TransformAndLog
)

from sciencebeam_utils.utils.csv import (
    csv_delimiter_by_filename
)


def get_logger():
    return logging.getLogger(__name__)


def DictToList(fields):
    def wrapper(x):
        get_logger().debug('DictToList: %s -> %s', fields, x)
        return [x.get(field) for field in fields]
    return wrapper


def _to_text(value):
    try:
        return text_type(value, encoding='utf-8')
    except TypeError:
        return text_type(value)


def format_csv_rows(rows, delimiter=','):
    get_logger().debug('format_csv_rows, rows: %s', rows)
    out = StringIO()
    writer = csv.writer(out, delimiter=text_type(delimiter))
    writer.writerows([
        [_to_text(x) for x in row]
        for row in rows
    ])
    result = out.getvalue().rstrip('\r\n')
    get_logger().debug('format_csv_rows, result: %s', result)
    return result


class WriteDictCsv(beam.PTransform):
    def __init__(self, path, columns, file_name_suffix=None):
        super(WriteDictCsv, self).__init__()
        self.path = path
        self.columns = columns
        self.file_name_suffix = file_name_suffix
        self.delimiter = csv_delimiter_by_filename(path + file_name_suffix)

    def expand(self, pcoll):  # pylint: disable=arguments-differ
        return (
            pcoll |
            "ToList" >> beam.Map(DictToList(self.columns)) |
            "Format" >> TransformAndLog(
                beam.Map(lambda x: format_csv_rows([x], delimiter=self.delimiter)),
                log_prefix='formatted csv: ',
                log_level='debug'
            ) |
            "Utf8Encode" >> beam.Map(lambda x: x.encode('utf-8')) |
            "Write" >> WriteToText(
                self.path,
                file_name_suffix=self.file_name_suffix,
                header=format_csv_rows([self.columns], delimiter=self.delimiter).encode('utf-8')
            )
        )


def _strip_quotes(s):
    return s[1:-1] if len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s

# copied and modified from https://github.com/pabloem/beam_utils
# (move back if still active)


class ReadLineIterator(object):
    def __init__(self, obj):
        self._obj = obj

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        line = self._obj.readline().decode('utf-8')
        if line is None or line == '':
            raise StopIteration
        return line


class CsvFileSource(FileBasedSource):
    """ A source for a GCS or local comma-separated-file
    Parses a text file assuming newline-delimited lines,
    and comma-delimited fields. Assumes UTF-8 encoding.
    """

    def __init__(  # pylint: disable=too-many-arguments
            self, file_pattern,
            compression_type=CompressionTypes.AUTO,
            delimiter=',', header=True, dictionary_output=True,
            validate=True, limit=None):
        """ Initialize a CsvFileSource.
        Args:
          delimiter: The delimiter character in the CSV file.
          header: Whether the input file has a header or not.
            Default: True
          dictionary_output: The kind of records that the CsvFileSource outputs.
            If True, then it will output dict()'s, if False it will output list()'s.
            Default: True
        Raises:
          ValueError: If the input arguments are not consistent.
        """
        super(CsvFileSource, self).__init__(
            file_pattern,
            compression_type=compression_type,
            validate=validate,
            splittable=False  # Can't just split anywhere
        )
        self.delimiter = delimiter
        self.header = header
        self.dictionary_output = dictionary_output
        self.limit = limit
        self._file = None

        if not self.header and dictionary_output:
            raise ValueError(
                'header is required for the CSV reader to provide dictionary output'
            )

    def read_records(self, file_name, range_tracker):  # noqa: E501 pylint: disable=arguments-differ,unused-argument
        # If a multi-file pattern was specified as a source then make sure the
        # start/end offsets use the default values for reading the entire file.
        headers = None
        self._file = self.open_file(file_name)

        reader = csv.reader(ReadLineIterator(self._file), delimiter=text_type(self.delimiter))

        line_no = 0
        for i, row in enumerate(reader):
            if self.header and i == 0:
                headers = row
                continue

            if self.limit and line_no >= self.limit:
                break

            line_no += 1
            if self.dictionary_output:
                yield {
                    header: value
                    for header, value in zip(headers, row)
                }
            else:
                yield row


class ReadDictCsv(beam.PTransform):
    """
    Simplified CSV parser, which does not support:
    * multi-line values
    * delimiter within value
    """

    def __init__(self, filename, header=True, limit=None):
        super(ReadDictCsv, self).__init__()
        if not header:
            raise RuntimeError('header required')
        self.filename = filename
        self.columns = None
        self.delimiter = csv_delimiter_by_filename(filename)
        self.limit = limit
        self.row_num = 0

    def expand(self, pcoll):  # pylint: disable=arguments-differ
        return (
            pcoll |
            beam.io.Read(CsvFileSource(
                self.filename,
                delimiter=self.delimiter,
                limit=self.limit
            ))
        )
