from __future__ import division

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

from apache_beam.io.filesystems import FileSystems

from sciencebeam_utils.utils.file_list import (
    load_file_list
)

from sciencebeam_utils.tools.tool_utils import (
  setup_logging,
  add_limit_args,
  add_default_args,
  process_default_args
)


LOGGER = logging.getLogger(__name__)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        'Check file list'
    )

    source = parser.add_argument_group('source')
    source.add_argument(
        '--file-list', type=str, required=True,
        help='path to source file list (tsv/csv/lst)'
    )
    source.add_argument(
        '--file-column', type=str, required=False,
        default='url',
        help='csv/tsv column (ignored for plain file list)'
    )

    add_limit_args(parser)
    add_default_args(parser)

    return parser.parse_args(argv)


def map_file_list_to_file_exists(file_list):
    with ThreadPoolExecutor(max_workers=50) as executor:
        return list(executor.map(FileSystems.exists, file_list))


def format_file_list(file_list):
    return '%s' % file_list


def format_file_exists_results(file_exists, file_list):
    if not file_exists:
        return 'empty file list'
    file_exists_count = sum(file_exists)
    file_missing_count = len(file_exists) - file_exists_count
    files_missing = [s for s, exists in zip(file_list, file_exists) if not exists]
    return (
        'files exist: %d (%.0f%%), files missing: %d (%.0f%%)%s' % (
            file_exists_count, 100.0 * file_exists_count / len(file_exists),
            file_missing_count, 100.0 * file_missing_count / len(file_exists),
            (
                ' (example missing: %s)' % format_file_list(files_missing[:3])
                if files_missing
                else ''
            )
        )
    )


def check_files_and_report_result(file_list):
    file_exists = map_file_list_to_file_exists(file_list)
    LOGGER.info('%s', format_file_exists_results(file_exists, file_list))
    assert sum(file_exists) > 0


def run(opt):
    file_list = load_file_list(
        opt.file_list,
        column=opt.file_column,
        limit=opt.limit
    )
    check_files_and_report_result(file_list)


def main(argv=None):
    args = parse_args(argv)

    process_default_args(args)

    run(args)


if __name__ == '__main__':
    setup_logging()

    main()
