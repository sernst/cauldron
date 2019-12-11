from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestUiStatuses(FlaskResultsTest):
    """Test suite for the ui_statuses module."""

    @patch('cauldron.cli.server.routes.ui_statuses.statuses.get_status')
    def test_get_status(self, get_status: MagicMock):
        """Should return the expected JSON status data."""
        get_status.return_value = {'foo': 'bar'}
        result = self.post('/ui-status', {})
        assert {'foo': 'bar'} == result.flask.get_json()
