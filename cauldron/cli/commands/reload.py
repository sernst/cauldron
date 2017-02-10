import os
import typing
from argparse import ArgumentParser

import cauldron
from cauldron import runner
from cauldron import session
from cauldron.environ import Response

NAME = 'reload'
DESCRIPTION = (
    """
    Discards all shared data and reloads the currently open project to its
    initial state
    """
)


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
        response: Response
) -> Response:

    project_before = cauldron.project.internal_project

    if not project_before:
        return response.fail(
            code='NO_PROJECT_FOUND',
            message='Unable to find a project'
        ).console(
            whitespace=1
        ).response

    path = project_before.source_directory
    if not os.path.exists(path):
        return response.fail(
            code='MISSING_PROJECT_PATH',
            message='The specified path does not exist',
            path=path
        ).console(
            whitespace=1
        ).response

    # Don't need the reference to the old version of the project anymore so
    # let the garbage collector have it
    project_before = None

    try:
        runner.initialize(path)
    except FileNotFoundError as err:
        return response.fail(
            code='PROJECT_INIT_FAILURE',
            message='Unable to initialize results',
            error=err
        ).console(
            '[Error]: Project not found',
            whitespace=1
        ).response

    project = cauldron.project.internal_project

    if project.results_path:
        session.initialize_results_path(project.results_path)

    project.write()

    return response.notify(
        kind='SUCCESS',
        code='RELOADED',
        message='Project "{}" has been reloaded'.format(project.title),
        path=path
    ).console(
        whitespace=1
    ).response
