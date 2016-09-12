from argparse import ArgumentParser
import typing

import cauldron
from cauldron import environ
from cauldron import session
from cauldron.environ import Response

NAME = 'refresh'
DESCRIPTION = """
    Rewrites the current state of the project to the results directory for
    viewing. Useful when you want to update support files.
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


def execute(
        parser: ArgumentParser,
        response: Response = None
):
    """

    :return:
    """

    project = cauldron.project
    if project:
        project = project.internal_project

    if not project:
        environ.log(
            '[ABORTED]: No project is open. Unable to refresh.',
            whitespace=1
        )
        return

    session.initialize_results_path(project.results_path)
    project.write()

    environ.log(
        '[COMPLETE]: Project display refreshed',
        whitespace=1
    )



