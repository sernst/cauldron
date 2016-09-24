import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.environ import Response
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

    parser.add_argument(
        '-t', '--temporary',
        dest='temporary',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When this option is included, the alias will only remain for this
            cauldron session. It will not be remembered for future sessions.
            """)
    )


def execute(
        parser: ArgumentParser,
        response: Response,
        command: str = None,
        name: str = None,
        path: str = None,
        temporary: bool = False
):
    """

    :return:
    """

    if name:
        name = name.replace(' ', '_').strip('"').strip()

    if path:
        path = environ.paths.clean(path.strip('"'))
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
    temporary_aliases = environ.configs.session.get('folder_aliases', {})
    persistent_aliases = environ.configs.persistent.get('folder_aliases', {})

    if not name and command in ['add', 'remove']:
        return response.fail(
            code='MISSING_ARG',
            message='You need to specify the name of the alias'
        ).console(
            whitespace=1
        ).response

    if command == 'list':
        items = []
        aliases = dict(
            list(temporary_aliases.items()) +
            list(persistent_aliases.items())
        )

        for k, v in aliases.items():
            items.append('{}\n   {}'.format(k, v['path']))
        environ.log_header('EXISTING ALIASES')
        environ.log(items)
        return response

    aliases = temporary_aliases if temporary else persistent_aliases

    if command == 'add':
        aliases[name] = dict(
            path=path
        )
        environ.configs.put(
            persists=not bool(temporary),
            folder_aliases=aliases
        )
        return response.notify(
            kind='ADDED',
            code='ALIAS_ADDED',
            message='The alias "{}" has been saved'.format(name)
        ).console(
            whitespace=1
        ).response

    if command == 'remove':
        if name in aliases:
            del aliases[name]
        environ.configs.put(
            persists=not bool(temporary),
            folder_aliases=aliases
        )

        return response.notify(
            kind='REMOVED',
            code='ALIAS_REMOVED',
            message='The alias "{}" has been removed'.format(name)
        ).console(
            whitespace=1
        ).response

    return response.fail(
        code='UNKNOWN_COMMAND',
        message='Unrecognized alias command "{}"'.format(command)
    ).console(
        whitespace=1
    ).response


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
