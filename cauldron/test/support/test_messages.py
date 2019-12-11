from cauldron.environ.response import Response
from cauldron.test.support import messages


def test_message():
    """Should echo message when printed."""
    r = Response()
    m = messages.Message(
        'MESSAGE',
        'Test message',
        'with multiple args',
        data={'a': [1, 2, 3], 'b': True},
        response=r
    )

    assert str(m) == m.echo()
