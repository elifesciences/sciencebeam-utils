from __future__ import absolute_import

import logging
import sys
from contextlib import contextmanager

from tqdm import tqdm


class TqdmLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # noqa pylint: disable=bare-except
            self.handleError(record)


def _is_console_logging_handler(handler):
    return isinstance(handler, logging.StreamHandler) and handler.stream in {sys.stdout, sys.stderr}


def _get_console_formatter(handlers):
    for handler in handlers:
        if _is_console_logging_handler(handler):
            return handler.formatter
    return None


@contextmanager
def redirect_logging_to_tqdm(logger=None):
    if logger is None:
        logger = logging.root
    tqdm_handler = TqdmLoggingHandler()
    original_handlers = logger.handlers
    tqdm_handler.setFormatter(_get_console_formatter(original_handlers))
    try:
        logger.handlers = [
            handler
            for handler in logger.handlers
            if not _is_console_logging_handler(handler)
        ] + [tqdm_handler]
        yield
    finally:
        logger.handlers = original_handlers


@contextmanager
def tqdm_with_logging_redirect(*args, **kwargs):
    logger = kwargs.pop('logger', None)
    with tqdm(*args, **kwargs) as pbar:
        with redirect_logging_to_tqdm(logger=logger):
            yield pbar
