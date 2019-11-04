import random
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui import launcher


@patch('time.sleep')
@patch('socket.socket')
@patch('webbrowser.open_new')
def test_opener_thread(
    open_new: MagicMock,
    socket_constructor: MagicMock,
    sleep: MagicMock,
):
    """Should wait for socket connection and then open web browser."""
    socket = MagicMock()
    socket.connect_ex.side_effect = [True, True, False]
    socket_constructor.return_value = socket

    thread = launcher.OpenUiOnStart(host='me', port=123)
    thread.start()
    thread.join()

    assert 2 == thread.retries, """
        Expect two attempts before it finally succeeds.
        """
    assert 'http://me:123/' == thread.root_url, """
        Expect the url to be composed of the values passed to the 
        thread's constructor.
        """
    assert 1 == open_new.call_count, """
        Expect the web browser open to eventually be called.
        """
    assert thread.retries == sleep.call_count, """
        Expect sleep to be called between each retry attempt.
        """
    assert (thread.retries + 1) == socket.connect_ex.call_count, """
        Expect the socket to be checked on each attempt.
        """


@patch('cauldron.ui.launcher._check_usage')
def test_find_open_port(_check_usage: MagicMock):
    """Should return 12 as the first open port."""
    expected = random.randint(0, 20)
    _check_usage.side_effect = [p < expected for p in range(30)]
    result = launcher.find_open_port('foo', range(30))
    assert expected == result, """
        Expect the first port not to be used to be port {}.
        """.format(expected)
