import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron import invoke


class TestInvoke(unittest.TestCase):
    """Test suite for the cauldron.invoke module"""

    def test_initialize(self):
        """Should initialize cauldron"""
        result = invoke.initialize()
        self.assertIsNotNone(result)

    @patch('cauldron.invoke.get_cauldron_module')
    def test_initialize_fail(self, get_cauldron_module: MagicMock):
        """Should fail to initialize cauldron"""
        get_cauldron_module.return_value = None

        with self.assertRaises(ImportError):
            invoke.initialize()

    @patch('cauldron.invoke.get_cauldron_module')
    def test_initialize_first_fail(self, get_cauldron_module: MagicMock):
        """Should fail to initialize cauldron"""
        returns = [{}, None]

        def mock_get_cauldron_module():
            return returns.pop()

        get_cauldron_module.side_effect = mock_get_cauldron_module
        result = invoke.initialize()
        self.assertIsNotNone(result)

    def test_get_cauldron_module(self):
        """Should successfully get cauldron module"""
        result = invoke.get_cauldron_module()
        self.assertIsNotNone(result)

    def test_get_cauldron_module_fail(self):
        """Should fail to get cauldron module"""
        with patch('cauldron.invoke.import_module') as import_module:
            import_module.side_effect = ImportError('Fake')
            result = invoke.get_cauldron_module()
        self.assertIsNone(result)

    @patch('cauldron.invoke.sys.exit')
    def test_run(self, sys_exit: MagicMock):
        """Should run the specified command"""
        sys_exit.side_effect = SystemExit('FAKE')

        with self.assertRaises(SystemExit):
            invoke.run(['--version'])

        self.assertLessEqual(1, sys_exit.call_count)
