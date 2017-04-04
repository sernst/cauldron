from cauldron.cli.server import arguments
from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestArguments(FlaskResultsTest):
    """ """

    def test_mocked_request(self):
        """ """

        result = arguments.from_request('invalid-request-value')
        self.assertIsInstance(result, dict)
