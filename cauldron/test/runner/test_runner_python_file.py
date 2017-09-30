from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.runner import python_file
from cauldron.test.support import scaffolds


class TestRunnerPythonFile(scaffolds.ResultsTest):
    """Test suite for the runner.python_file module"""

    @patch('functools.partial')
    def test_get_file_contents_failed(self, partial: MagicMock):
        """Should return code that raises IOError if unable to open file"""

        partial.return_value = MagicMock(side_effect=IOError('FAKE'))
        result = python_file.get_file_contents('FAKE')
        self.assertTrue(result.startswith('raise IOError('))
