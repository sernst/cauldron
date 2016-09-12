from argparse import ArgumentParser

from cauldron import environ
from cauldron.environ import Response

NAME = 'exit'
DESCRIPTION = 'Exit the cauldron shell'


def execute(parser: ArgumentParser, response: Response = None):
    """

    :param parser:
    :return:
    """

    environ.configs.save()
    environ.output.end()
