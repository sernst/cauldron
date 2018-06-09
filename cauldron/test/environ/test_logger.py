from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.environ import logger


@patch('cauldron.environ.logger.log')
def test_header_zero(log: MagicMock):
    """Should log a level zero header without modification"""
    logger.header('hello', level=0)
    args = log.call_args[0]
    assert 'hello' == args[0], 'Message should not be modified'


@patch('cauldron.environ.logger.log')
def test_header_infinity(log: MagicMock):
    """Should log a high level header without modification"""
    logger.header('hello', level=8)
    args = log.call_args[0]
    assert 'hello' == args[0], 'Message should not be modified'


@patch('cauldron.environ.logger.raw')
def test_log_with_kwargs(raw: MagicMock):
    """Should include kwargs in log output"""
    message = logger.log('test', foo=42)
    assert 1 == raw.call_count
    assert 0 < message.find('foo: 42'), """
        Expected to find the foo kwarg in the message.
        """


@patch('traceback.extract_tb')
def test_get_error_stack_module(extract_tb: MagicMock):
    """Should nullify location when the location is module"""
    frame = MagicMock()
    frame.name = '<module>'
    extract_tb.return_value = [frame]
    result = logger.get_error_stack()
    assert result[0]['location'] is None, """
        Expected a <module> value to be changed to `None`.
        """


@patch('traceback.extract_tb')
def test_get_error_stack(extract_tb: MagicMock):
    """Should remove prefix when location is a remote shared library path"""
    frame = MagicMock()
    frame.name = '/tmp/cd-remote/__cauldron_shared_libs/test'
    extract_tb.return_value = [frame]
    result = logger.get_error_stack()
    assert result[0]['location'] == '/test', """
        Expected the remote prefix to be removed.
        """
