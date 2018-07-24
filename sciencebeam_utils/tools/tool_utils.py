import logging


def setup_logging():
    logging.basicConfig(level='INFO')
    logging.getLogger('oauth2client').setLevel('WARNING')


def add_limit_args(parser):
    parser.add_argument(
        '--limit', type=int, required=False,
        help='limit the files to process'
    )


def add_default_args(parser):
    parser.add_argument(
        '--debug', action='store_true', default=False,
        help='enable debug output'
    )


def process_default_args(args):
    if args.debug:
        logging.getLogger().setLevel('DEBUG')
