from __future__ import absolute_import

from contextlib import contextmanager
from mock import patch

import pytest

import apache_beam as beam
from apache_beam.testing.util import assert_that, equal_to

from sciencebeam_utils.beam_utils.testing import (
    TestPipeline,
    BeamTest,
    MockWriteToText,
    patch_beam_io
)

from sciencebeam_utils.beam_utils.csv import (
    WriteDictCsv,
    ReadDictCsv,
    format_csv_rows
)


MODULE_UNDER_TEST = 'sciencebeam_utils.beam_utils.csv'

UNICODE_STR_1 = u'file1\u1234.pdf'


@contextmanager
def patch_module_under_test(**kwargs):
    with patch.multiple(
        MODULE_UNDER_TEST,
        **kwargs
    ) as mocks:
        yield mocks


def to_csv(rows, delimiter):
    return (format_csv_rows(rows, delimiter).replace('\r\n', '\n') + '\n').encode('utf-8')


class TestFormatCsvRows:
    def test_should_format_empty_rows(self):
        assert format_csv_rows([]) == ''

    def test_should_format_single_unicode_cell(self):
        assert format_csv_rows([[UNICODE_STR_1]]) == UNICODE_STR_1

    def test_should_format_single_byte_cell(self):
        assert format_csv_rows([[UNICODE_STR_1.encode('utf-8')]]) == UNICODE_STR_1

    def test_should_format_single_int_cell(self):
        assert format_csv_rows([[123]]) == '123'

    def test_should_format_single_string_row(self):
        assert format_csv_rows([['abc', 'def']]) == 'abc,def'

    def test_should_format_multiple_string_rows(self):
        assert (
            format_csv_rows([['abc', 'def'], ['123', '456']]).splitlines()
            == ['abc,def', '123,456']
        )


@pytest.mark.slow
class TestWriteDictCsv(BeamTest):
    def test_should_write_tsv_with_header(self, test_context):
        with patch_module_under_test(WriteToText=MockWriteToText):
            with TestPipeline() as p:
                _ = (  # noqa: F841
                    p |
                    beam.Create([{
                        'a': 'a1',
                        'b': 'b1'
                    }]) |
                    WriteDictCsv(
                        '.temp/dummy',
                        ['a', 'b'],
                        '.tsv'
                    )
                )
            assert test_context.get_file_content('.temp/dummy.tsv') == to_csv([
                ['a', 'b'],
                ['a1', 'b1']
            ], '\t')


@pytest.mark.slow
class TestReadDictCsv(BeamTest):
    def test_should_read_rows_as_dict(self, test_context):
        with patch_beam_io():
            test_context.set_file_content('.temp/dummy.tsv', to_csv([
                ['a', 'b'],
                ['a1', 'b1']
            ], '\t'))

            with TestPipeline() as p:
                result = (
                    p |
                    ReadDictCsv('.temp/dummy.tsv')
                )
                assert_that(result, equal_to([{
                    'a': 'a1',
                    'b': 'b1'
                }]))

    def test_should_read_multiple(self, test_context):
        with patch_beam_io():
            test_context.set_file_content('.temp/dummy.tsv', to_csv([
                ['a', 'b'],
                ['a1', 'b1'],
                ['a2', 'b2'],
                ['a3', 'b3']
            ], '\t'))

            with TestPipeline() as p:
                result = (
                    p |
                    ReadDictCsv('.temp/dummy.tsv')
                )
                assert_that(result, equal_to([{
                    'a': 'a1',
                    'b': 'b1'
                }, {
                    'a': 'a2',
                    'b': 'b2'
                }, {
                    'a': 'a3',
                    'b': 'b3'
                }]))

    def test_should_limit_number_of_rows(self, test_context):
        with patch_beam_io():
            test_context.set_file_content('.temp/dummy.tsv', to_csv([
                ['a', 'b'],
                ['a1', 'b1'],
                ['a2', 'b2'],
                ['a3', 'b3']
            ], '\t'))

            with TestPipeline() as p:
                result = (
                    p |
                    ReadDictCsv('.temp/dummy.tsv', limit=2)
                )
                assert_that(result, equal_to([{
                    'a': 'a1',
                    'b': 'b1'
                }, {
                    'a': 'a2',
                    'b': 'b2'
                }]))
