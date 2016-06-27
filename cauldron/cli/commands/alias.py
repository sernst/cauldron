import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.interaction import autocompletion

NAME = 'alias'
DESCRIPTION = """
    Add or remove a path alias to make opening projects easier
    """


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    parser.add_argument(
        'command',
        type=str,
        default=None,
        help=cli.reformat("""
            The specific alias command to execute. One of: add, remove or list.
            """)
    )

    parser.add_argument(
        'name',
        type=str,
        nargs='?',
        default=None,
        help=cli.reformat("""
            The name of the alias on which to act if needed by the specific
            command.
            """)
    )

    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default=None,
        help=cli.reformat("""
            The path for the alias when using the add command
            """)
    )


def execute(
        parser: ArgumentParser,
        command: str = None,
        name: str = None,
        path: str = None
):
    """

    :return:
    """

    if name:
        name = name.replace(' ', '_')

    if path:
        path = environ.paths.clean(path)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
            environ.log(
                """
                [WARNING]: The specified path was not a directory. Aliases must
                    be directories, so the directory containing the specified
                    file will be used instead:

                    {}
                """.format(path),
                whitespace=1
            )

    environ.configs.load()
    aliases = environ.configs.fetch('folder_aliases', {})

    if not name and command in ['add', 'remove']:
        environ.log('[ERROR]: You need to specify the name of the alias')
        return

    if command == 'list':
        items = []
        for k, v in aliases.items():
            items.append('{}\n   {}'.format(k, v['path']))
        environ.log_header('EXISTING ALIASES')
        environ.log(items)
        return

    if command == 'add':
        aliases[name] = dict(
            path=path
        )
        environ.configs.put(persists=True, folder_aliases=aliases)
        environ.log(
            '[ADDED]: The alias "{}" has been saved'.format(name),
            whitespace=1
        )
        return

    if command == 'remove':
        if name in aliases:
            del aliases[name]
        environ.configs.put(persists=True, folder_aliases=aliases)
        environ.log(
            '[REMOVED]: The alias "{}" has been removed'.format(name),
            whitespace=1
        )
        return

    environ.log(
        '[ERROR]: Unrecognized alias command "{}"'.format(command),
        whitespace=1
    )


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if len(parts) < 2:
        return autocompletion.matches(segment, parts[-1] if parts else '', [
            'add',
            'remove',
            'list'
        ])

    if len(parts) < 3:
        environ.configs.load()
        aliases = environ.configs.fetch('folder_aliases', {})
        return autocompletion.matches(
            segment,
            parts[-1],
            aliases.keys()
        )

    return autocompletion.match_path(segment, parts[-1])
