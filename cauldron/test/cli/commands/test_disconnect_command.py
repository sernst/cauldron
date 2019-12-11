from unittest.mock import patch
from unittest.mock import MagicMock
from requests import exceptions as request_exceptions

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestDisconnectCommand(scaffolds.ResultsTest):
    """..."""

    def test_disconnected(self):
        """Should fail if no url is provided in the command."""

        r = support.run_command('disconnect')
        self.assertFalse(r.failed)

    def test_autocomplete(self):
        """Should return empty options for autocomplete."""

        result = support.autocomplete('disconnect')
        self.assertEqual(len(result), 0)