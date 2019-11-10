import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands import ls
from cauldron.environ import Response

NAME = 'cd'
DESCRIPTION = 'Change current directory.'
SYNCHRONOUS = True


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """Populate the argument parser for the ls command invocation."""
    parser.add_argument('directory')


def execute(
        context: cli.CommandContext,
        directory: str = '.',
) -> Response:
    """Executes the cd command."""
    clean_directory = environ.paths.clean(directory.strip('"').strip("'"))
    try:
        os.chdir(clean_directory)
    except FileNotFoundError as error:
        return (
            context.response
            .fail(
                code='NO_SUCH_DIRECTORY',
                message='No such directory "{}"'.format(clean_directory),
                error=error
            )
            .console(whitespace=1)
            .response
        )
    except PermissionError as error:
        return (
            context.response
            .fail(
                code='PERMISSION_DENIED',
                message='Access denied to "{}"'.format(clean_directory),
                error=error
            )
            .console(whitespace=1)
            .response
        )

    # Update the directory that is used for general reference
    # within the application state.
    environ.configs.put(persists=False, directory=clean_directory)

    return ls.execute(context)
