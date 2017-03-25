from cauldron import cli
from cauldron import environ
from cauldron.environ import Response

NAME = 'exit'
DESCRIPTION = 'Exit the cauldron shell'


def execute(context: cli.CommandContext) -> Response:
    """ """

    environ.configs.save()
    return context.response.end()
