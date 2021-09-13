import os
import errno


def makedirs(path, exist_ok=False):
    try:
        # Python 3
        os.makedirs(path, exist_ok=exist_ok)
    except TypeError:
        # Python 2
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path) and exist_ok:
                pass
            else:
                raise
