import sys
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands import clear
from cauldron.cli.commands import configure
from cauldron.cli.commands import exit
from cauldron.cli.commands import export
from cauldron.cli.commands import open
from cauldron.cli.commands import purge
from cauldron.cli.commands import run
from cauldron.cli.commands import status

ME = sys.modules[__name__]


def split_line(line: str) -> typing.Tuple[str, str]:
    """
    Separates the raw line string into two strings: (1) the command and (2) the
    argument(s) string

    :param line:
    :return:
    """

    index = line.find(' ')
    if index == -1:
        return line.lower(), ''

    return line[:index].lower(), line[index:].strip()


def explode_line(raw:str) -> typing.List[str]:
    """

    :param raw:
    :return:
    """

    raw = raw.strip()
    out = ['']
    breaker = ' '

    for index in range(len(raw)):
        c = raw[index]
        out[-1] += c

        if c == breaker:
            out[-1] = out[-1].strip()
            out.append('')
            breaker = ' '
        elif c == '"' and breaker == ' ':
            breaker = '"'
            continue

    return [x for x in out if len(x) > 0]


def get_parser(name: str) -> ArgumentParser:
    """

    :param name:
    :return:
    """
    try:
        module = getattr(ME, name)
    except Exception:
        return None

    description = None
    if hasattr(module, 'DESCRIPTION'):
        description = getattr(module, 'DESCRIPTION')

    parser = ArgumentParser(
        prog=name,
        add_help=False,
        description=description
    )

    try:
        if hasattr(module, 'populate'):
            getattr(module, 'populate')(parser)
    except Exception as err:
        print(err)
        return None

    parser.add_argument(
        '-h', '--help',
        dest='show_help',
        action='store_true',
        default=False,
        help=cli.reformat("""
            Print this help information instead of running the command
            """)
    )

    return parser


def execute(name: str, raw_args: str):
    """

    :return:
    """

    if not hasattr(ME, name):
        environ.log(
            """
            [ERROR]: "{name}" is not a recognized command.
            For a list of available commands run:

                >>> cauldron help
            """)
        return None


    try:
        module = getattr(ME, name)
        parser = get_parser(name)
    except Exception as err:
        return None
    if parser is None:
        return

    raw_args = explode_line(raw_args)

    for arg in raw_args:
        if arg in ['?', '-?', '--?', '-h', '--h', 'help', '-help', '--help']:
            parser.print_help()
            return None

    try:
        command_args = vars(parser.parse_args(raw_args))
    except SystemExit:
        parser.print_help()
        return None

    if command_args['show_help']:
        parser.print_help()
        return

    if 'show_help' in command_args:
        del command_args['show_help']

    return getattr(module, 'execute')(parser=parser, **command_args)


def list_command_names():
    """

    :return:
    """

    out = []
    for key in dir(ME):
        item = getattr(ME, key)
        if item and hasattr(item, 'DESCRIPTION'):
            out.append(key)

    return out


def print_module_help():
    """

    :return:
    """

    print(' ')
    for key in dir(ME):
        item = getattr(ME, key)
        if hasattr(item, 'DESCRIPTION'):
            msg = '[{key}]:\n   {description}'.format(
                key=key,
                description=cli.reformat(
                    getattr(item, 'DESCRIPTION')
                ).replace('\n', '\n   ')
            )

            environ.log(msg)


def show_help(command_name:str = None):
    """ Prints the basic command help to the console """

    if command_name and hasattr(ME, command_name):
        parser = get_parser(command_name)
        if parser is not None:
            parser.print_help()
            return

    environ.log('The following commands are available:')
    print_module_help()

    msg = """
        For more information on the various commands, enter help on the
        specific command:

            >>> [COMMAND] help
        """
    environ.log(msg, whitespace_top=1)


def autocomplete(
        command_name: str,
        prefix: str,
        line: str,
        begin_index: int,
        end_index: int
):
    """

    :param command_name:
    :param prefix:
    :param line:
    :param begin_index:
    :param end_index:
    :return:
    """

    if not hasattr(ME, command_name):
        return []

    parts = explode_line(line)[1:]

    try:
        module = getattr(ME, command_name)
        if hasattr(module, 'autocomplete'):
            out = getattr(module, 'autocomplete')(prefix, line, parts)
            if out is not None:
                return out
    except Exception as err:
        print(err)

    return []
