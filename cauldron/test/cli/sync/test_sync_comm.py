import os
from unittest.mock import MagicMock
from unittest.mock import patch

from requests import Response as HttpResponse

from cauldron import environ
from cauldron.cli.sync import comm
from cauldron.test import support
from cauldron.test.support import scaffolds


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

    @patch('requests.get')
    def test_failed_download(self, requests_get: MagicMock):
        """ should fail to download if the GET request raises an exception """

        requests_get.side_effect = IOError('FAKE ERROR')

        path = self.get_temp_path('failed_download', 'fake.filename')
        response = comm.download_file('fake.filename', path)

        self.assert_has_error_code(response, 'CONNECTION_ERROR')
        self.assertFalse(os.path.exists(path))

    @patch('requests.get')
    def test_failed_download_write(self, requests_get: MagicMock):
        """ should fail to download if the GET request raises an exception """

        requests_get.return_value = dict()
        path = self.get_temp_path('failed_download', 'fake.filename')

        with patch('builtins.open') as open_func:
            open_func.side_effect = IOError('Fake Error')
            response = comm.download_file('fake.filename', path)

        self.assert_has_error_code(response, 'WRITE_ERROR')
        self.assertFalse(os.path.exists(path))

    @patch('requests.get')
    def test_download(self, requests_get: MagicMock):
        """ should successfully download saved cauldron file """

        def mock_iter_content(*args, **kwargs):
            yield from [b'a', b'b', b'', None, b'c']

        http_response = HttpResponse()
        http_response.iter_content = mock_iter_content
        requests_get.return_value = http_response

        path = self.get_temp_path('failed_download', 'fake.filename')
        response = comm.download_file('fake.filename', path)

        self.assertTrue(response.success)
        self.assertTrue(os.path.exists(path))

        with open(path, 'rb') as f:
            contents = f.read()
        self.assertEqual(contents, b'abc')

