import json

from flask import Response as FlaskResponse

from cauldron.test.support import server
from cauldron.test.support.scaffolds import ResultsTest


class FlaskResultsTest(ResultsTest):
    """Parent class for Flask application related testing."""

    def setUp(self):
        super(FlaskResultsTest, self).setUp()
        self.app = server.create_test_app()

    def get(self, endpoint: str, **kwargs) -> server.Responses:
        """ send get request to the test flask application."""
        return server.get(self.app, endpoint, **kwargs)

    def post(self, endpoint: str, data = None, **kwargs) -> server.Responses:
        """ send post request to the test flask application."""
        return server.post(self.app, endpoint, data, **kwargs)
