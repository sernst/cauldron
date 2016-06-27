from argparse import ArgumentParser
import typing

from cauldron import environ

NAME = 'exit'
DESCRIPTION = """
    Exit the cauldron shell.
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
    pass


def execute(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    environ.configs.save()
    environ.output.end()
