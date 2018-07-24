
from __future__ import absolute_import

import os

from apache_beam.io.filesystems import FileSystems


def get_ext(filename):
    name, ext = os.path.splitext(filename)
    if ext == '.gz':
        ext = get_ext(name) + ext
    return ext


def strip_ext(filename):
    # strip of gz, assuming there will be another extension before .gz
    if filename.endswith('.gz'):
        filename = filename[:-3]
    return os.path.splitext(filename)[0]


def relative_path(base_path, path):
    if not base_path:
        return path
    if not base_path.endswith('/'):
        base_path += '/'
    return path[len(base_path):] if path.startswith(base_path) else path


def is_relative_path(path):
    return not path.startswith('/') and '://' not in path


def join_if_relative_path(base_path, path):
    return (
        FileSystems.join(base_path, path)
        if base_path and is_relative_path(path)
        else path
    )


def change_ext(path, old_ext, new_ext):
    if old_ext is None:
        old_ext = os.path.splitext(path)[1]
        if old_ext == '.gz':
            path = path[:-len(old_ext)]
            old_ext = os.path.splitext(path)[1]
    if old_ext and path.endswith(old_ext):
        return path[:-len(old_ext)] + new_ext
    return path + new_ext


def get_output_file(filename, source_base_path, output_base_path, output_file_suffix):
    return FileSystems.join(
        output_base_path,
        change_ext(
            relative_path(source_base_path, filename),
            None, output_file_suffix
        )
    )


def base_path_for_file_list(file_list):
    common_prefix = os.path.commonprefix(file_list)
    i = max(common_prefix.rfind('/'), common_prefix.rfind('\\'))
    if i >= 0:
        return common_prefix[:i]
    return ''


def get_or_validate_base_path(file_list, base_path):
    common_path = base_path_for_file_list(file_list)
    if base_path:
        if not common_path.startswith(base_path):
            raise AssertionError(
                "invalid base path '%s', common path is: '%s'" % (base_path, common_path)
            )
        return base_path
    return common_path
