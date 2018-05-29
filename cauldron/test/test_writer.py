import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron import writer


@patch('time.sleep')
@patch('cauldron.writer.attempt_file_write')
def test_write_file(attempt_file_write: MagicMock, sleep: MagicMock):
    """Should successfully write without retries"""
    attempt_file_write.return_value = None

    success, error = writer.write_file('fake', 'fake')
    assert success
    assert error is None
    assert 1 == attempt_file_write.call_count
    assert 0 == sleep.call_count


@patch('time.sleep')
@patch('cauldron.writer.attempt_file_write')
def test_write_file_fail(attempt_file_write: MagicMock, sleep: MagicMock):
    """Should fail to write with retries"""
    attempt_file_write.return_value = IOError('FAKE')

    success, error = writer.write_file('fake', 'fake', retry_count=5)
    assert not success
    assert error is not None
    assert 5 == attempt_file_write.call_count
    assert 5 == sleep.call_count


@patch('time.sleep')
@patch('cauldron.writer.attempt_json_write')
def test_write_json(attempt_json_write: MagicMock, sleep: MagicMock):
    """Should successfully write JSON without retries"""
    attempt_json_write.return_value = None
    success, error = writer.write_json_file('fake', {})
    assert success
    assert error is None
    assert 1 == attempt_json_write.call_count
    assert 0 == sleep.call_count


@patch('time.sleep')
@patch('cauldron.writer.attempt_json_write')
def test_write_json_fail(attempt_json_write: MagicMock, sleep: MagicMock):
    """Should fail to write JSON data to file with retries"""
    attempt_json_write.return_value = IOError('FAKE')
    success, error = writer.write_json_file('fake', {}, retry_count=5)
    assert not success
    assert error is not None
    assert 5 == attempt_json_write.call_count
    assert 5 == sleep.call_count


def test_attempt_file_write():
    """Should write to file without error"""
    with patch('builtins.open'):
        result = writer.attempt_file_write('fake', 'fake')
    assert result is None


def test_attempt_file_write_failed():
    """Should fail to write to file"""
    with patch('builtins.open') as open_func:
        open_func.side_effect = IOError('Fake')
        result = writer.attempt_file_write('fake', 'fake')
    assert result is not None


def test_attempt_json_write():
    """Should write to JSON file without error"""
    with patch('builtins.open'):
        result = writer.attempt_json_write('fake', {})
    assert result is None


def test_attempt_json_write_failed():
    """Should fail to write JSON data to file"""
    with patch('builtins.open') as open_func:
        open_func.side_effect = IOError('Fake')
        result = writer.attempt_json_write('fake', {})
    assert result is not None


def test_write_offset_binary():
    """Should write binary data correctly to the given offset"""
    path = tempfile.mkstemp()[-1]
    try:
        writer.write_file(path, b'abc', 'wb')
        writer.write_file(path, b'def', 'ab', offset=1)
        writer.write_file(path, b'ghi', 'w+b', offset=2)
        writer.write_file(path, b'jkl', 'a+b', offset=3)

        with open(path, 'rb') as f:
            contents = f.read()
    except Exception:  # pragma: no cover
        raise
    finally:
        environ.systems.remove(path, 10)

    assert b'adgjkl' == contents, """
        Expected the offset argument to adjust how data is written
        to the file to produce an overlapped result.
        """


def test_write_offset_ascii():
    """Should write string data correctly to the given offset"""
    path = tempfile.mkstemp()[-1]
    try:
        writer.write_file(path, 'abc', 'w')
        writer.write_file(path, 'def', 'a', offset=1)
        writer.write_file(path, '\u00A9hi', 'w', offset=2)
        writer.write_file(path, '\u0113kl', 'a', offset=4)

        with open(path, 'rb') as f:
            contents = f.read().decode()
    except Exception:  # pragma: no cover
        raise
    finally:
        environ.systems.remove(path, 10)

    assert 'ad\u00A9\u0113kl' == contents, """
        Expected the offset argument to adjust how data is written
        to the file to produce an overlapped result.
        """
