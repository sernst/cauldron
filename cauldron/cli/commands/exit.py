from argparse import ArgumentParser

from cauldron import environ

NAME = 'exit'
DESCRIPTION = 'Exit the cauldron shell'


def execute(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    environ.configs.save()
    environ.output.end()
