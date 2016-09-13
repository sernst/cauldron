from argparse import ArgumentParser

from cauldron import environ
from cauldron.environ import Response

NAME = 'exit'
DESCRIPTION = 'Exit the cauldron shell'


def execute(parser: ArgumentParser, response: Response) -> Response:
    """

    :param parser:
    :param response:
    :return:
    """

    environ.configs.save()
    return response.end()
