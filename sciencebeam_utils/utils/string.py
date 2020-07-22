from future.utils import python_2_unicode_compatible


@python_2_unicode_compatible
class LazyStr:
    def __init__(self, fn):
        self.fn = fn

    def __str__(self):
        return self.fn()


def parse_list(s, sep=','):
    s = s.strip()
    if not s:
        return []
    return [item.strip() for item in s.split(sep)]
