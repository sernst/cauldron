from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.runner import python_file
from cauldron.test.support import scaffolds


@patch('cauldron.runner.python_file.functools')
def test_get_file_contents_failed(functools: MagicMock):
    """Should return code that raises IOError if unable to open file"""
    func = MagicMock()
    func.side_effect = IOError
    functools.partial.return_value = func
    result = python_file.get_file_contents('FAKE')
    assert result.startswith('raise IOError(')
