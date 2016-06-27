import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.configure import actions

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


def execute(
        parser: ArgumentParser,
        key: str = None,
        value: typing.List[str] = None,
        list_all: bool = False,
        remove: bool = False
):
    """

    :return:
    """

    environ.configs.load()

    if key is None:
        if list_all:
            actions.echo_all()
        else:
            parser.print_help()
        return

    if not value:
        if remove:
            actions.remove_key(key)
        else:
            actions.echo_key(key)
    else:
        actions.set_key(key, value)


