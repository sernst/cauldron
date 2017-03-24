import typing

from cauldron import cli
from cauldron import environ
from cauldron.environ import Response


NAME = 'disconnect'
DESCRIPTION = """
    Disconnect from the remote cauldron server and restore shell to local
    control
    """


def execute(context: cli.CommandContext) -> Response:
    """

    :return:
    """

    environ.remote_connection = environ.RemoteConnection(
        active=False,
        url=None
    )

    return context.response.notify(
        kind='SUCCESS',
        code='DISCONNECTED',
        message='Disconnected from remote cauldron'
    ).console(
        whitespace=1
    ).response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    return []
