import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron import writer


class TestWriter(unittest.TestCase):
    """Test suite for the cauldron.writer module"""

    @patch('time.sleep')
    @patch('cauldron.writer.attempt_file_write')
    def test_write_file(self, attempt_file_write: MagicMock, sleep: MagicMock):
        """Should successfully write without retries"""

        attempt_file_write.return_value = None

        success, error = writer.write_file('fake', 'fake')
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(1, attempt_file_write.call_count)
        self.assertEqual(0, sleep.call_count)

    @patch('time.sleep')
    @patch('cauldron.writer.attempt_file_write')
    def test_write_file_fail(
            self,
            attempt_file_write: MagicMock,
            sleep: MagicMock
    ):
        """Should fail to write with retries"""

        attempt_file_write.return_value = IOError('FAKE')

        success, error = writer.write_file('fake', 'fake', retry_count=5)
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertEqual(5, attempt_file_write.call_count)
        self.assertEqual(5, sleep.call_count)

    @patch('time.sleep')
    @patch('cauldron.writer.attempt_json_write')
    def test_write_json(self, attempt_json_write: MagicMock, sleep: MagicMock):
        """Should successfully write JSON without retries"""

        attempt_json_write.return_value = None

        success, error = writer.write_json_file('fake', {})
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(1, attempt_json_write.call_count)
        self.assertEqual(0, sleep.call_count)

    @patch('time.sleep')
    @patch('cauldron.writer.attempt_json_write')
    def test_write_json_fail(
            self,
            attempt_json_write: MagicMock,
            sleep: MagicMock
    ):
        """Should fail to write JSON data to file with retries"""

        attempt_json_write.return_value = IOError('FAKE')

        success, error = writer.write_json_file('fake', {}, retry_count=5)
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertEqual(5, attempt_json_write.call_count)
        self.assertEqual(5, sleep.call_count)

    def test_attempt_file_write(self):
        """Should write to file without error"""

        with patch('builtins.open'):
            result = writer.attempt_file_write('fake', 'fake')
        self.assertIsNone(result)

    def test_attempt_file_write_failed(self):
        """Should fail to write to file"""

        with patch('builtins.open') as open_func:
            open_func.side_effect = IOError('Fake')
            result = writer.attempt_file_write('fake', 'fake')
        self.assertIsNotNone(result)

    def test_attempt_json_write(self):
        """Should write to JSON file without error"""

        with patch('builtins.open'):
            result = writer.attempt_json_write('fake', {})
        self.assertIsNone(result)

    def test_attempt_json_write_failed(self):
        """Should fail to write JSON data to file"""

        with patch('builtins.open') as open_func:
            open_func.side_effect = IOError('Fake')
            result = writer.attempt_json_write('fake', {})
        self.assertIsNotNone(result)
