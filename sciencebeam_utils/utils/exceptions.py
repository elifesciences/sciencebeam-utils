import pickle


class SerializableException(RuntimeError):
    pass


def is_serializable(obj) -> bool:
    try:
        pickle.dumps(obj)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def get_serializable_exception(exception: BaseException) -> BaseException:
    if is_serializable(exception):
        return exception
    serializable_exception = SerializableException(str(exception))
    serializable_exception.__cause__ = get_serializable_exception(exception.__cause__)
    serializable_exception.__context__ = get_serializable_exception(exception.__context__)
    serializable_exception.__traceback__ = exception.__traceback__
    return serializable_exception
