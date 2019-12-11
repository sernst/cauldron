from unittest.mock import patch

from cauldron.invoke import invoker
from cauldron.invoke import parser


def run_command(command: str) -> int:
    """Executes the specified command by parsing the args and running them."""
    args = parser.parse(command.split(' '))

    with patch('cauldron.invoke.invoker._pre_run_updater'):
        return invoker.run(args.get('command'), args)
