from argparse import ArgumentParser

from cauldron import environ
from cauldron import runner

NAME = 'close'
DESCRIPTION = """
    Close the currently opened project
    """


def execute(parser: ArgumentParser):
    """

    :return:
    """

    if runner.close():
        environ.output.notify(
            kind='SUCCESS',
            code='PROJECT_CLOSED',
            message='Project has been closed'
        ).console(whitespace=1)
    else:
        environ.output.notify(
            kind='ABORTED',
            code='NO_OPEN_PROJECT',
            message='There was no open project to close'
        ).console(whitespace=1)
