from unittest.mock import patch

import cauldron
from cauldron.cli.server import run as server_runner
from cauldron.cli.shell import CauldronShell
from cauldron.test.support import scaffolds


class TestInit(scaffolds.ResultsTest):
    """

    """

    def test_get_env_info(self):
        """
        """

        result = cauldron.get_environment_info()
        self.assertIsInstance(result, dict)
        self.assertTrue('cauldron' in result)

    def test_run_shell(self):
        """
        """

        with patch.object(CauldronShell, 'cmdloop') as cmd_loop:
            cauldron.run_shell()
            self.assertTrue(cmd_loop.call_count == 1)

    def test_run_server(self):
        """
        """

        with patch.object(server_runner, 'execute') as server_execute:
            cauldron.run_server()
            server_execute.assert_called_once_with(port=5010, debug=False)

    def test_run_server_custom_args(self):
        """
        """

        kwargs = dict(port=8000, debug=True, host='www.some-host-name.com')

        with patch.object(server_runner, 'execute') as server_execute:
            cauldron.run_server(**kwargs)
            server_execute.assert_called_once_with(**kwargs)
