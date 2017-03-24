from collections import namedtuple
from unittest.mock import patch
from unittest.mock import MagicMock
from requests import exceptions as request_exceptions

from cauldron import environ
from cauldron.test import support
from cauldron.test.support import scaffolds


MockResponse = namedtuple('MockResponse', ['status_code'])


class TestConnectCommand(scaffolds.ResultsTest):
    """ """

    def test_no_url(self):
        """ should fail if no url is provided in the command """

        r = support.run_command('connect')
        self.assertTrue(r.failed, support.Message(
            'CONNECT-FAIL',
            'Should fail to run connect command when no url is provided',
            response=r
        ))

    @patch('requests.get')
    def test_invalid_url_error(self, requests_get: MagicMock):
        """ should fail if the url is not valid """

        requests_get.side_effect = request_exceptions.InvalidURL('Fake')

        r = support.run_command('connect "a url"')
        self.assert_has_error_code(r, 'INVALID_URL')

    @patch('requests.get')
    def test_connection_error(self, requests_get: MagicMock):
        """ should fail if the url cannot be connected to """

        requests_get.side_effect = request_exceptions.ConnectionError('Fake')

        r = support.run_command('connect "a url"')
        self.assert_has_error_code(r, 'CONNECTION_ERROR')

    @patch('requests.get')
    def test_other_error(self, requests_get: MagicMock):
        """ should fail if the get request raises an unknown exception """

        requests_get.side_effect = ValueError('Fake')

        r = support.run_command('connect http://some.url')
        self.assert_has_error_code(r, 'CONNECT_COMMAND_ERROR')

    @patch('requests.get')
    def test_bad_status_code(self, requests_get: MagicMock):
        """ should fail if the get request does not have a 200 status code """

        requests_get.return_value = MockResponse(status_code=500)

        r = support.run_command('connect http://some.url')
        self.assert_has_error_code(r, 'CONNECTION_ERROR')

    @patch('requests.get')
    def test_valid(self, requests_get: MagicMock):
        """ should succeed to get ping data from remove cauldron kernel """

        requests_get.return_value = MockResponse(200)
        url_raw = 'something.com'
        r = support.run_command('connect {}'.format(url_raw))
        self.assertFalse(r.failed, support.Message('Failed', response=r))

        url_clean = r.data['url']
        self.assertTrue(
            url_clean.startswith('http://'),
            support.Message('Schema', response=r)
        )
        self.assertLess(
            0,
            url_clean.index(url_raw),
            support.Message('Modified Url', response=r)
        )

        self.assertTrue(environ.remote_connection.active)
        self.assertEqual(environ.remote_connection.url, url_clean)

        support.run_command('disconnect')

    def test_autocomplete(self):
        """ should return empty options for autocomplete """

        result = support.autocomplete('connect')
        self.assertEqual(len(result), 0)
