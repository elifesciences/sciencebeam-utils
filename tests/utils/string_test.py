from sciencebeam_utils.utils.string import (
    parse_list
)


class TestParseList:
    def test_should_return_empty_list_for_empty_string(self):
        assert parse_list('') == []

    def test_should_return_single_item(self):
        assert parse_list('abc') == ['abc']

    def test_should_return_multiple_items(self):
        assert parse_list('abc,def') == ['abc', 'def']

    def test_should_ignore_space(self):
        assert parse_list(' abc , def ') == ['abc', 'def']
