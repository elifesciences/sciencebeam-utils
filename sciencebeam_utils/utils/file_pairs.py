import logging
import os
from functools import reduce  # pylint: disable=redefined-builtin

from apache_beam.io.filesystems import FileSystems

from sciencebeam_utils.utils.collection import (
    groupby_to_dict,
    sort_and_groupby_to_dict
)

from .file_path import strip_ext


LOGGER = logging.getLogger(__name__)


def find_matching_filenames(pattern):
    return (x.path for x in FileSystems.match([pattern])[0].metadata_list)


def group_files_by_parent_directory(filenames):
    return groupby_to_dict(sorted(filenames), os.path.dirname)


def group_files_by_name_excl_ext(filenames):
    return sort_and_groupby_to_dict(filenames, strip_ext)


def zip_by_keys(*dict_list):
    keys = reduce(lambda agg, v: agg | set(v.keys()), dict_list, set())
    return (
        [d.get(k) for d in dict_list]
        for k in sorted(keys)
    )


def group_file_pairs_by_parent_directory_or_name(files_by_type):
    grouped_files_by_pattern = [
        group_files_by_parent_directory(files) for files in files_by_type
    ]
    for files_in_group_by_pattern in zip_by_keys(*grouped_files_by_pattern):
        if all(len(files or []) == 1 for files in files_in_group_by_pattern):
            yield tuple([files[0] for files in files_in_group_by_pattern])
        else:
            grouped_by_name = [
                group_files_by_name_excl_ext(files or [])
                for files in files_in_group_by_pattern
            ]
            for files_by_name in zip_by_keys(*grouped_by_name):
                if all(len(files or []) == 1 for files in files_by_name):
                    yield tuple([files[0] for files in files_by_name])
                else:
                    LOGGER.info(
                        'no exclusively matching files found: %s',
                        list(files_by_name)
                    )


def find_file_pairs_grouped_by_parent_directory_or_name(patterns):
    matching_files_by_pattern = [
        list(find_matching_filenames(pattern)) for pattern in patterns
    ]
    LOGGER.info(
        'found number of files %s',
        ', '.join(
            '%s: %d' % (pattern, len(files))
            for pattern, files in zip(patterns, matching_files_by_pattern)
        )
    )
    patterns_without_files = [
        pattern
        for pattern, files in zip(patterns, matching_files_by_pattern)
        if len(files) == 0
    ]
    if patterns_without_files:
        raise RuntimeError('no files found for: %s' % patterns_without_files)
    return group_file_pairs_by_parent_directory_or_name(
        matching_files_by_pattern
    )
