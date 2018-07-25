import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.invoke import parser
from cauldron.invoke import invoker


def run_command(command: str) -> int:
    """Executes the specified command by parsing the args and running them"""
    full_command = 'cauldron {}'.format(command).strip()
    args = parser.parse(full_command.split(' '))
    return invoker.run(args.get('command'), args)


class TestInvoker(unittest.TestCase):
    """Test suite for the cauldron.invoke.invoker module"""

    def test_run_version(self):
        """Should run the version command without error"""
        result = run_command('version')
        self.assertEqual(0, result)

    @patch('cauldron.cli.server.run.execute')
    def test_run_kernel(self, server_execute: MagicMock):
        """Should start the kernel"""
        result = run_command('kernel')
        self.assertEqual(0, result)

    @patch('cauldron.cli.shell.CauldronShell.cmdloop')
    def test_run_shell(self, cmdloop: MagicMock):
        """Should run shell"""
        result = run_command('shell')
        self.assertEqual(0, result)
        self.assertEqual(1, cmdloop.call_count)

    @patch('cauldron.invoke.invoker.in_project_directory')
    @patch('cauldron.cli.shell.CauldronShell.cmdloop')
    def test_run_shell_with_open(
            self,
            cmdloop: MagicMock,
            in_project_directory: MagicMock
    ):
        """Should run shell with open command"""
        in_project_directory.return_value = True

        result = run_command('shell')
        self.assertEqual(0, result)
        self.assertEqual(1, cmdloop.call_count)

    @patch('cauldron.cli.shell.CauldronShell.cmdloop')
    @patch('cauldron.invoke.invoker.run_batch')
    def test_run_shell_batch(self, run_batch: MagicMock, cmdloop: MagicMock):
        """Should run batch from shell command"""
        run_batch.return_value = 42

        result = run_command('shell --project=fake')
        self.assertEqual(42, result)
        self.assertEqual(1, run_batch.call_count)
        self.assertEqual(0, cmdloop.call_count)

    @patch('cauldron.cli.batcher.run_project')
    def test_run_batch(self, run_project: MagicMock):
        """Should run batch project"""
        result = invoker.run_batch({})
        self.assertEqual(0, result)

    def test_load_shared_data_none(self):
        """Should return empty dictionary when value is None"""
        result = invoker.load_shared_data(None)
        self.assertIsInstance(result, dict)

    def test_load_shared_data_missing(self):
        """Should raise an exception if file not found"""
        with self.assertRaises(FileNotFoundError):
            invoker.load_shared_data('nosuchfileorpath')

    @patch('os.path.exists')
    def test_load_shared_data_open_error(self, exists: MagicMock):
        """Should raise error if unable to read file"""
        exists.return_value = True

        with self.assertRaises(IOError):
            invoker.load_shared_data('fakepaththatexists')

    @patch('json.load')
    def test_load_shared_data_data_error(self, json_load: MagicMock):
        """Should raise error if JSON isn't a dictionary"""
        json_load.return_value = []

        with self.assertRaises(ValueError):
            invoker.load_shared_data(__file__)

    @patch('json.load')
    def test_load_shared_data(self, json_load: MagicMock):
        """Should raise error if JSON isn't a dictionary"""
        json_load.return_value = {}

        result = invoker.load_shared_data(__file__)
        self.assertIsInstance(result, dict)

    def test_no_such_command(self):
        """Should return error code if the command is not recognized"""
        result = invoker.run('fake', {'parser': MagicMock()})
        self.assertEqual(1, result)
