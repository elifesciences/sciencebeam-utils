import argparse
import logging

from sciencebeam_utils.utils.file_list import (
    load_file_list,
    save_file_list,
    to_relative_file_list
)

from sciencebeam_utils.utils.file_path import (
    join_if_relative_path,
    get_or_validate_base_path,
    get_output_file
)

from sciencebeam_utils.tools.check_file_list import (
    DEFAULT_EXAMPLE_COUNT,
    check_files_and_report_result
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
        'Get output files based on source files and suffix.'
    )

    source = parser.add_argument_group('source')
    source.add_argument(
        '--source-file-list', type=str, required=True,
        help='path to source file list (tsv/csv/lst)'
    )
    source.add_argument(
        '--source-file-column', type=str, required=False,
        default='url',
        help='csv/tsv column (ignored for plain file list)'
    )
    source.add_argument(
        '--source-base-path', type=str, required=False,
        help='base data path for source file urls'
    )

    output = parser.add_argument_group('output')
    output.add_argument(
        '--output-file-list', type=str, required=True,
        help='path to output file list (tsv/csv/lst)'
    )
    output.add_argument(
        '--output-file-column', type=str, required=False,
        default='url',
        help='csv/tsv column (ignored for plain file list)'
    )
    output.add_argument(
        '--output-file-suffix', type=str, required=False,
        help='file suffix (will be added to source urls after removing ext)'
    )
    output.add_argument(
        '--output-base-path', type=str, required=False,
        help='base output path (by default source base path with"-results" suffix)'
    )
    output.add_argument(
        '--use-relative-paths', action='store_true',
        help='create a file list with relative paths (relative to the output data path)'
    )

    add_limit_args(parser)

    parser.add_argument(
        '--check', action='store_true', default=False,
        help='check whether the output files exist'
    )
    parser.add_argument(
        '--check-limit', type=int, required=False,
        help='limit the files to check'
    )
    parser.add_argument(
        '--example-count', type=int, required=False,
        default=DEFAULT_EXAMPLE_COUNT,
        help='number of missing examples to display'
    )

    add_default_args(parser)

    return parser.parse_args(argv)


def get_output_file_list(file_list, source_base_path, output_base_path, output_file_suffix):
    return [
        get_output_file(filename, source_base_path, output_base_path, output_file_suffix)
        for filename in file_list
    ]


def run(opt):
    source_file_list = load_file_list(
        join_if_relative_path(
            opt.source_base_path,
            opt.source_file_list
        ),
        column=opt.source_file_column,
        limit=opt.limit
    )
    source_base_path = get_or_validate_base_path(
        source_file_list, opt.source_base_path
    )

    target_file_list = get_output_file_list(
        source_file_list, source_base_path, opt.output_base_path, opt.output_file_suffix
    )

    if opt.check:
        check_file_list = (
            target_file_list[:opt.check_limit] if opt.check_limit
            else target_file_list
        )
        LOGGER.info(
            'checking %d (out of %d) files...',
            len(check_file_list), len(target_file_list)
        )
        check_files_and_report_result(
            check_file_list,
            example_count=opt.example_count
        )

    if opt.use_relative_paths:
        target_file_list = to_relative_file_list(opt.output_base_path, target_file_list)

    LOGGER.info(
        'saving file list (with %d files) to: %s',
        len(target_file_list), opt.output_file_list
    )
    save_file_list(
        opt.output_file_list,
        target_file_list,
        column=opt.output_file_column
    )


def process_args(args):
    if not args.output_base_path:
        args.output_base_path = args.source_base_path + '-results'


def main(argv=None):
    args = parse_args(argv)

    process_default_args(args)
    process_args(args)

    run(args)


if __name__ == '__main__':
    setup_logging()

    main()
