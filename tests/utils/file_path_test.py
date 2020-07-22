import pytest

from sciencebeam_utils.utils.file_path import (
    relative_path,
    join_if_relative_path,
    change_ext,
    get_output_file,
    base_path_for_file_list,
    get_or_validate_base_path
)


class TestRelativePath:
    def test_should_return_path_if_base_path_is_none(self):
        assert relative_path(None, 'file') == 'file'

    def test_should_return_path_if_path_outside_base_path(self):
        assert relative_path('/parent', '/other/file') == '/other/file'

    def test_should_return_absolute_path_if_base_path_matches(self):
        assert relative_path('/parent', '/parent/file') == 'file'


class TestJoinIfRelativePath:
    def test_should_return_path_if_base_path_is_none(self):
        assert join_if_relative_path(None, 'file') == 'file'

    def test_should_return_path_if_not_relative(self):
        assert join_if_relative_path('/parent', '/other/file') == '/other/file'

    def test_should_return_joined_path_if_relative(self):
        assert join_if_relative_path('/parent', 'file') == '/parent/file'


class TestChangeExt:
    def test_should_replace_simple_ext_with_simple_ext(self):
        assert change_ext('file.pdf', None, '.xml') == 'file.xml'

    def test_should_replace_simple_ext_with_combined_ext(self):
        assert change_ext('file.pdf', None, '.svg.zip') == 'file.svg.zip'

    def test_should_remove_gz_ext_before_replacing_ext(self):
        assert change_ext('file.pdf.gz', None, '.svg.zip') == 'file.svg.zip'


class TestGetOutputFile:
    def test_should_return_output_file_with_path_and_change_ext(self):
        assert get_output_file(
            '/source/path/file.pdf',
            '/source',
            '/output',
            '.xml'
        ) == '/output/path/file.xml'


class TestBasePathForFileList:
    def test_should_return_empty_string_if_file_list_is_empty(self):
        assert base_path_for_file_list([]) == ''

    def test_should_return_empty_string_if_filename_is_empty(self):
        assert base_path_for_file_list(['']) == ''

    def test_should_return_parent_directory_of_single_file(self):
        assert base_path_for_file_list(['/base/path/1/file']) == '/base/path/1'

    def test_should_return_common_path_of_two_files(self):
        assert base_path_for_file_list(['/base/path/1/file', '/base/path/2/file']) == '/base/path'

    def test_should_return_common_path_of_two_files_using_protocol(self):
        assert base_path_for_file_list([
            'a://base/path/1/file', 'a://base/path/2/file'
        ]) == 'a://base/path'

    def test_should_return_common_path_of_two_files_using_forward_slash(self):
        assert base_path_for_file_list([
            '\\base\\path\\1\\file', '\\base\\path\\2\\file'
        ]) == '\\base\\path'

    def test_should_return_empty_string_if_no_common_path_was_found(self):
        assert base_path_for_file_list(['a://base/path/1/file', 'b://base/path/2/file']) == ''

    def test_should_return_common_path_ignoring_partial_name_match(self):
        assert base_path_for_file_list(['/base/path/file1', '/base/path/file2']) == '/base/path'


class TestGetOrValidateBasePath:
    def test_should_return_base_path_of_two_files_if_no_base_path_was_provided(self):
        assert get_or_validate_base_path(
            ['/base/path/1/file', '/base/path/2/file'],
            None
        ) == '/base/path'

    def test_should_return_passed_in_base_path_if_valid(self):
        assert get_or_validate_base_path(
            ['/base/path/1/file', '/base/path/2/file'],
            '/base'
        ) == '/base'

    def test_should_raise_error_if_passed_in_base_path_is_invalid(self):
        with pytest.raises(AssertionError):
            get_or_validate_base_path(
                ['/base/path/1/file', '/base/path/2/file'],
                '/base/other'
            )
