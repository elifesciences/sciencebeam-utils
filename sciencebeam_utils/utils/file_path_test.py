from .file_path import (
    relative_path,
    join_if_relative_path,
    change_ext,
    get_output_file
)


class TestRelativePath(object):
    def test_should_return_path_if_base_path_is_none(self):
        assert relative_path(None, 'file') == 'file'

    def test_should_return_path_if_path_outside_base_path(self):
        assert relative_path('/parent', '/other/file') == '/other/file'

    def test_should_return_absolute_path_if_base_path_matches(self):
        assert relative_path('/parent', '/parent/file') == 'file'


class TestJoinIfRelativePath(object):
    def test_should_return_path_if_base_path_is_none(self):
        assert join_if_relative_path(None, 'file') == 'file'

    def test_should_return_path_if_not_relative(self):
        assert join_if_relative_path('/parent', '/other/file') == '/other/file'

    def test_should_return_joined_path_if_relative(self):
        assert join_if_relative_path('/parent', 'file') == '/parent/file'


class TestChangeExt(object):
    def test_should_replace_simple_ext_with_simple_ext(self):
        assert change_ext('file.pdf', None, '.xml') == 'file.xml'

    def test_should_replace_simple_ext_with_combined_ext(self):
        assert change_ext('file.pdf', None, '.svg.zip') == 'file.svg.zip'

    def test_should_remove_gz_ext_before_replacing_ext(self):
        assert change_ext('file.pdf.gz', None, '.svg.zip') == 'file.svg.zip'


class TestGetOutputFile(object):
    def test_should_return_output_file_with_path_and_change_ext(self):
        assert get_output_file(
            '/source/path/file.pdf',
            '/source',
            '/output',
            '.xml'
        ) == '/output/path/file.xml'
