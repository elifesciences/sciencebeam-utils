from sciencebeam_utils.utils.file_pairs import group_file_pairs_by_parent_directory_or_name


class TestGroupFilePairsByParentDirectoryOrName:
    def test_should_return_empty_list_with_empty_input_file_lists(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            [],
            []
        ])) == []

    def test_should_group_single_file(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file.x'],
            ['parent1/file.y']
        ])) == [('parent1/file.x', 'parent1/file.y')]

    def test_should_group_single_file_in_directory_with_different_names(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file1.x'],
            ['parent1/file2.y']
        ])) == [('parent1/file1.x', 'parent1/file2.y')]

    def test_should_ignore_files_in_different_directories(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file.x'],
            ['parent2/file.y']
        ])) == []

    def test_should_group_multiple_files_in_separate_parent_directories(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file.x', 'parent2/file.x'],
            ['parent1/file.y', 'parent2/file.y']
        ])) == [
            ('parent1/file.x', 'parent1/file.y'),
            ('parent2/file.x', 'parent2/file.y')
        ]

    def test_should_group_multiple_files_in_same_parent_directory_with_same_name(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file1.x', 'parent1/file2.x'],
            ['parent1/file1.y', 'parent1/file2.y']
        ])) == [
            ('parent1/file1.x', 'parent1/file1.y'),
            ('parent1/file2.x', 'parent1/file2.y')
        ]

    def test_should_group_multiple_files_in_same_parent_directory_with_same_name_gzipped(self):
        assert list(group_file_pairs_by_parent_directory_or_name([
            ['parent1/file1.x.gz', 'parent1/file2.x.gz'],
            ['parent1/file1.y.gz', 'parent1/file2.y.gz']
        ])) == [
            ('parent1/file1.x.gz', 'parent1/file1.y.gz'),
            ('parent1/file2.x.gz', 'parent1/file2.y.gz')
        ]
