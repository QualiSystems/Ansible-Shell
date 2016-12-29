from mock import Mock


def mock_enter_exit_self():
    f = Mock()
    f.__enter__ = Mock(return_value=f)
    f.__exit__ = Mock()
    return f


def mock_enter_exit(returned_value):
    f = Mock()
    f.__enter__ = Mock(return_value=returned_value)
    f.__exit__ = Mock()
    return f


class Any(object):
    def __init__(self, predicate=None):
        self.predicate = predicate
    def __eq__(self, other):
        return not self.predicate or self.predicate(other)
