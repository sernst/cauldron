from argparse import ArgumentParser

from cauldron import environ
from cauldron import runner
from cauldron.environ import Response

NAME = 'close'
DESCRIPTION = """
    Close the currently opened project
    """


def execute(parser: ArgumentParser, response: Response) -> Response:
    """

    :return:
    """

    if runner.close():
        return response.notify(
            kind='SUCCESS',
            code='PROJECT_CLOSED',
            message='Project has been closed'
        ).console(
            whitespace=1
        ).response

    return response.notify(
        kind='ABORTED',
        code='NO_OPEN_PROJECT',
        message='There was no open project to close'
    ).console(
        whitespace=1
    ).response
