import os
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.environ.response import Response
from cauldron.test.support import scaffolds
from cauldron.cli import sync


class TestSyncFiles(scaffolds.ResultsTest):
    """ Tests for the cauldron.cli.sync.files module """

    @patch('os.path.getmtime')
    @patch('cauldron.cli.sync.files.send_chunk')
    def test_send_not_modified(
            self,
            send_chunk: MagicMock,
            getmtime: MagicMock
    ):
        """ should not sync file if it does not need to be synced """

        file_path = 'fake.path'
        getmtime.return_value = 900

        response = sync.files.send(
            file_path=file_path,
            relative_path=file_path,
            newer_than=1000
        )

        getmtime.assert_called_once_with(file_path)
        send_chunk.assert_not_called()

        self.assert_has_success_code(response, 'NOT_MODIFIED')

    @patch('cauldron.cli.sync.files.send_chunk')
    def test_send_progress(self, send_chunk: MagicMock):
        """ should send file in multiple chunks """

        send_chunk.return_value = Response()

        file_path = os.path.realpath(__file__)
        size = os.path.getsize(file_path)
        chunk_size = int(size / 3)
        chunk_count = sync.io.get_file_chunk_count(file_path, chunk_size)

        response = sync.files.send(
            file_path=file_path,
            relative_path=__file__,
            chunk_size=chunk_size
        )

        self.assertTrue(response.success)
        self.assertGreaterEqual(chunk_count, len(response.messages))

    @patch('cauldron.cli.sync.files.send_chunk')
    def test_failed_chunk(self, send_chunk: MagicMock):
        """ should abort sending when chunk write fails """

        send_chunk.return_value = Response().fail().response
        file_path = os.path.realpath(__file__)

        response = sync.files.send(
            file_path=file_path,
            relative_path=__file__
        )

        self.assertTrue(response.failed)

    @patch('cauldron.cli.sync.files.send')
    def test_all_failed_file(self, send: MagicMock):
        """ should abort sending when file send fails """

        send.return_value = Response().fail().response
        directory = os.path.dirname(os.path.realpath(__file__))

        response = sync.files.send_all_in(directory)

        self.assertTrue(response.failed)
