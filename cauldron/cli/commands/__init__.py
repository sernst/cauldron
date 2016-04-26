import re
import sys
import typing
from argparse import ArgumentParser

from cauldron import environ
from cauldron import cli
from cauldron.cli.commands import clear
from cauldron.cli.commands import configure
from cauldron.cli.commands import purge
from cauldron.cli.commands import exit
from cauldron.cli.commands import open
from cauldron.cli.commands import run
from cauldron.cli.commands import export

ME = sys.modules[__name__]


def explode_args(raw_args:str) -> typing.List[str]:
    """

    :param raw_args:
    :return:
    """
    try:
        raw_args = re.compile('\s{2,}').sub(' ', raw_args).split()
        return [x.strip() for x in raw_args]
    except Exception:
        return []


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
        parser = ArgumentParser(
            prog=name,
            description=getattr(module, 'DESCRIPTION')
        )

        if hasattr(module, 'populate'):
            getattr(module, 'populate')(parser)
    except Exception as err:
        print(err)
        return None

    raw_args = explode_args(raw_args)

    for arg in raw_args:
        if arg in ['?', '-?', '--?', '-h', '--h', 'help', '-help', '--help']:
            parser.print_help()
            return None

    try:
        command_args = vars(parser.parse_args(raw_args))
    except SystemExit:
        parser.print_help()
        return None

    return getattr(module, 'execute')(parser=parser, **command_args)


def list_modules():
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


def show_help():
    """ Prints the basic command help to the console """

    environ.log('The following commands are available:')
    list_modules()

    msg = """
        For more information on the various commands, enter help on the
        specific command:

            >>> [COMMAND] help
        """
    environ.log(msg, whitespace_top=1)


def autocomplete(name: str, text: str, *args):
    """

    :param name:
    :param text:
    :param args:
    :return:
    """

    if len(text.strip()) == 0:
        return []

    if not hasattr(ME, name):
        return []

    entries = explode_args(text)

    try:
        module = getattr(ME, name)
        if hasattr(module, 'autocomplete'):
            out = getattr(module, 'autocomplete')(text, entries, *args)
            if out is not None:
                return out
    except Exception as err:
        print(err)

    return []
