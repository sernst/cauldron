from argparse import ArgumentParser

from cauldron import environ

DESCRIPTION = """
    Exit the cauldron shell.
"""


def populate(parser: ArgumentParser):
    pass


def execute(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    environ.configs.save()
    return True
