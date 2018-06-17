from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.session.writing import file_io
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestWriting(scaffolds.ResultsTest):
    """Test suite for the writing module"""

    def test_plotly_project(self):
        """Should properly write a project that has been run"""
        support.open_project(self, '@examples:time-gender')
        response = support.run_command('run')
        self.assertFalse(response.failed)

    def test_entry_from_dict_write_entry(self):
        """Should create a file write entry from the source dict."""
        result = file_io.entry_from_dict({'contents': 'abc', 'path': '/foo'})
        self.assertIsInstance(result, file_io.FILE_WRITE_ENTRY)
        self.assertEqual('abc', result.contents)
        self.assertEqual('/foo', result.path)

    def test_entry_from_dict_copy_entry(self):
        """Should create a file copy entry from the source dict."""
        result = file_io.entry_from_dict({
            'source': '/bar',
            'destination': '/foo'
        })
        self.assertIsInstance(result, file_io.FILE_COPY_ENTRY)
        self.assertEqual('/bar', result.source)
        self.assertEqual('/foo', result.destination)

    @patch('cauldron.session.writing.file_io.copy')
    @patch('cauldron.session.writing.file_io.write')
    def test_deploy(self, write: MagicMock, copy: MagicMock):
        """Should write and copy given entries according to type."""
        entries = [
            file_io.FILE_COPY_ENTRY('a', 'b'),
            file_io.FILE_WRITE_ENTRY('a', 'b'),
            None
        ]

        file_io.deploy(entries)
        self.assertEqual(1, write.call_count)
        self.assertEqual(entries[1], write.call_args[0][0])
        self.assertEqual(1, copy.call_count)
        self.assertEqual(entries[0], copy.call_args[0][0])

    def test_deploy_failed(self):
        """Should raise value error for invalid/unknown entries."""
        entries = ['not a valid entry']
        with self.assertRaises(ValueError):
            file_io.deploy(entries)

    @patch('time.sleep')
    @patch('shutil.copy2')
    def test_copy_retries(self, copy2: MagicMock, sleep: MagicMock):
        """Should fail to copy entry and raise an IOError."""
        copy2.side_effect = ValueError('FAKE')
        with self.assertRaises(IOError):
            file_io.copy(file_io.FILE_COPY_ENTRY(__file__, '/fake'))
        self.assertEqual(3, sleep.call_count)
