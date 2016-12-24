import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.configure import actions
from cauldron.environ import Response

NAME = 'configure'
DESCRIPTION = """
    View or modify the Cauldron's configuration settings
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
        'key',
        type=str,
        nargs='?',
        default=None,
        help=cli.reformat("""
            The configuration key to be modify
            """)
    )

    parser.add_argument(
        'value',
        type=str,
        nargs='*',
        default=None,
        help=cli.reformat("""
            The value to assign to the configuration key. If omitted, the
            currently stored value for this key will be displayed.
            """)
    )

    parser.add_argument(
        '-r', '--remove',
        dest='remove',
        action='store_true',
        default=False,
        help=cli.reformat("""
            When included, this flag indicates that the specified key should
            be removed from the cauldron configs file.
            """)
    )

    parser.add_argument(
        '-l', '--list',
        dest='list_all',
        action='store_true',
        default=False,
        help=cli.reformat("""
            This flag is only useful when no key and no value have been
            specified. In such a case, this command will list all keys and
            values currently stored in the configuration file.
            """)
    )

    parser.add_argument(
        '-f', '--forget',
        dest='forget',
        action='store_true',
        default=False,
        help=cli.reformat("""
            Specifies that the value should not persist beyond this session.
            """)
    )


def execute(
        parser: ArgumentParser,
        response: Response = None,
        key: str = None,
        value: typing.List[str] = None,
        list_all: bool = False,
        remove: bool = False,
        forget: bool = False
) -> Response:
    """

    :return:
    """

    environ.configs.load()

    if key is None:
        if list_all:
            actions.echo_all()
        else:
            parser.print_help()
        return response

    persists = (not forget)

    if not value:
        if remove:
            actions.remove_key(key, persists=persists)
        else:
            actions.echo_key(key)
    else:
        actions.set_key(key, value, persists=persists)

    return response
