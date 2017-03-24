from unittest.mock import patch
from unittest.mock import MagicMock
from requests import Response as HttpResponse

from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron import environ
from cauldron.cli.sync import comm


class TestSyncComm(scaffolds.ResultsTest):
    """ Tests for the cauldron.cli.sync.sync_comm module """

    def test_assemble_url_without_connection(self):
        """ should assemble url """

        endpoint = '/some-endpoint'
        url_assembled = comm.assemble_url(endpoint)
        self.assertEqual(
            url_assembled,
            'http://localhost:5010{}'.format(endpoint)
        )

    def test_assemble_url_specified_connection(self):
        """ should assemble url using the specified remote connection data """

        url = 'some.url:5451'
        endpoint = '/some-endpoint'
        remote_connection = environ.RemoteConnection(url=url, active=True)

        url_assembled = comm.assemble_url(endpoint, remote_connection)
        self.assertEqual(url_assembled, 'http://{}{}'.format(url, endpoint))

    def test_assemble_url_global_connection(self):
        """ should assemble url using the specified remote connection data """

        url = 'some.url:5451'
        endpoint = '/some-endpoint'

        support.run_command('connect {} --force'.format(url))

        url_assembled = comm.assemble_url(endpoint)
        self.assertEqual(url_assembled, 'http://{}{}'.format(url, endpoint))

        support.run_command('disconnect')

    @patch('requests.get')
    def test_send_request_invalid(self, request_get: MagicMock):
        """ should fail to send request """

        request_get.side_effect = ValueError('Fake Error')

        response = comm.send_request('/fake', method='get')
        self.assert_has_error_code(response, 'CONNECTION_ERROR')

    @patch('cauldron.cli.sync.comm.parse_http_response')
    @patch('requests.post')
    def test_send_request_valid(
            self,
            request_post: MagicMock,
            parse_http_response: MagicMock
    ):
        """ should fail to send request """

        request_post.return_value = HttpResponse()
        parse_http_response.return_value = environ.Response('test')

        response = comm.send_request(
            endpoint='/fake',
            method='post',
            data=dict(a=1, b=2)
        )
        self.assertEqual(response.identifier, 'test')

    def test_parse_valid_http_response(self):
        """ should fail to send request """

        source_response = environ.Response().update(test='hello_world')

        def json_mock(*args, **kwargs):
            return source_response.serialize()

        http_response = HttpResponse()
        http_response.json = json_mock

        response = comm.parse_http_response(http_response)

        self.assertEqual(
            source_response.data['test'],
            response.data['test']
        )

    def test_parse_invalid_http_response(self):
        """ should fail to parse invalid http response """

        http_response = HttpResponse()
        response = comm.parse_http_response(http_response)
        self.assert_has_error_code(response, 'INVALID_REMOTE_RESPONSE')
        self.assertEqual(http_response, response.http_response)
