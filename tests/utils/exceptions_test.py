from sciencebeam_utils.utils.exceptions import (
    is_serializable,
    get_serializable_exception
)


class SerializableException(RuntimeError):
    pass


class NotSerializableException(RuntimeError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._not_pickable = lambda: 1


class TestIsSerializable:
    def test_should_return_true_for_serializable_exception(self):
        assert is_serializable(SerializableException())

    def test_should_return_false_for_not_serializable_exception(self):
        assert not is_serializable(NotSerializableException())


class TestGetPickableException:
    def test_should_return_passed_in_serializable_exception(self):
        exception = SerializableException()
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception == exception
        assert is_serializable(serializable_exception)

    def test_should_return_serializable_exception_replacement_without_cause(self):
        exception = NotSerializableException("not serializable")
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception != exception
        assert str(serializable_exception) == str(exception)
        assert serializable_exception.__cause__ is None
        assert is_serializable(serializable_exception)

    def test_should_preserve_traceback(self):
        try:
            raise NotSerializableException("not serializable")
        except NotSerializableException as _exception:
            exception = _exception
        assert exception.__traceback__ is not None
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception != exception
        assert serializable_exception.__traceback__ == exception.__traceback__

    def test_should_return_serializable_exception_replacement_with_serializable_cause(self):
        base_exception = SerializableException("base")
        exception = NotSerializableException("not serializable")
        exception.__cause__ = base_exception
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception != exception
        assert str(serializable_exception) == str(exception)
        assert serializable_exception.__cause__ == base_exception
        assert is_serializable(serializable_exception)

    def test_should_return_serializable_exception_replacement_with_not_serializable_cause(self):
        base_exception = NotSerializableException("base")
        exception = NotSerializableException("not serializable")
        exception.__cause__ = base_exception
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception != exception
        assert str(serializable_exception) == str(exception)
        assert serializable_exception.__cause__ != base_exception
        assert str(serializable_exception.__cause__) == str(base_exception)
        assert is_serializable(serializable_exception)

    def test_should_return_serializable_exception_replacement_with_not_serializable_context(self):
        base_exception = NotSerializableException("base")
        exception = NotSerializableException("not serializable")
        exception.__context__ = base_exception
        serializable_exception = get_serializable_exception(exception)
        assert serializable_exception != exception
        assert str(serializable_exception) == str(exception)
        assert serializable_exception.__context__ != base_exception
        assert str(serializable_exception.__context__) == str(base_exception)
        assert is_serializable(serializable_exception)
