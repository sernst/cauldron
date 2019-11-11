import typing
from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import mark
from cauldron.environ.response import Response


def test_get_response():
    """Should get the response back from the response message."""
    r = Response()
    assert r == r.fail().get_response()


def test_warn():
    """Should notify if warned is called."""
    r = Response()
    r.warn('FAKE_WARN', key='VALUE')

    assert len(r.warnings) == 1
    assert r.warnings[0].message == 'FAKE_WARN'
    assert r.warnings[0].data['key'] == 'VALUE'


def test_debug_echo():
    """Should echo debug information"""
    r = Response()
    r.debug_echo()


def test_echo():
    """Should echo information"""
    r = Response()
    r.warn('WARNING', something=[1, 2, 3], value=False)
    r.fail('ERROR')
    result = r.echo()
    assert 0 < result.find('WARNING')
    assert 0 < result.find('ERROR')


def test_echo_parented():
    """Should call parent echo"""
    r = Response()
    parent = Response().consume(r)

    func = mock.MagicMock()
    with patch.object(parent, 'echo', func):
        r.echo()
        func.assert_any_call()


def test_consume_nothing():
    """Should abort consuming if there is nothing to consume"""
    r = Response()
    r.consume(None)


def test_grandparent():
    """Should parent correctly if parented"""
    child = Response()
    parent = Response()
    grandparent = Response()

    grandparent.consume(parent)
    parent.consume(child)

    assert child.parent == grandparent


def test_update_parented():
    """Should update through parent."""
    child = Response()
    parent = Response()
    parent.consume(child)

    child.update(banana='orange')
    assert parent.data['banana'] == 'orange'


def test_notify_parented():
    """Should notify through parent."""
    child = Response()
    parent = Response()
    parent.consume(child)

    child.notify('SUCCESS', 'Good Stuff', 'GO-CAULDRON')
    assert len(parent.messages) == 1

    m = parent.messages[0]
    assert m.code == 'GO-CAULDRON'
    assert m.kind == 'SUCCESS'
    assert m.message == 'Good Stuff'


def test_end_parented():
    """Should end the parent."""
    child = Response()
    parent = Response()
    parent.consume(child)

    child.end()
    assert parent.ended


def test_logging():
    """Should log messages to the log"""
    r = Response()
    r.notify(
        kind='TEST',
        code='TEST_MESSAGE',
        message='This is a test',
    ).console_header(
        'Harold'
    ).console(
        'Holly'
    ).console_raw('Handy')

    out = r.get_notification_log()
    assert -1 < out.find('Harold')
    assert -1 < out.find('Holly')
    assert -1 < out.find('Handy')

    r = Response.deserialize(r.serialize())
    compare = r.get_notification_log()
    assert out == compare


def test_self_consumption():
    """Should not consume itself and cause regression error"""
    r = Response()
    r.consume(r)


def test_join_nothing():
    """Should do nothing and return if no thread exists"""
    r = Response()
    assert not r.join()


def test_join_thread():
    """Should join the associated thread and return True"""
    r = Response()
    r.thread = MagicMock()
    assert r.join()
    assert 1 == r.thread.join.call_count


RETURNS_SCENARIO = [
    ([], None),
    ([1], 1),
    ([1, 'a', True], (1, 'a', True))
]


@mark.parametrize('args, expected', RETURNS_SCENARIO)
def test_returns(args: list, expected: typing.Any):
    """Should return the expected results after being set."""
    r = Response()
    r._last_updated = 0
    r.returns(*args)
    assert expected == r.returned
    assert 0 < r.last_updated, """
        Expect last updated to be greater than 0 after return values
        are set.
        """
