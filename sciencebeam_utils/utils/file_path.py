
from __future__ import absolute_import

import os

from apache_beam.io.filesystems import FileSystems


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
