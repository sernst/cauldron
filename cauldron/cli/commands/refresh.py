import typing
from argparse import ArgumentParser

import cauldron
from cauldron import session
from cauldron.environ import Response

NAME = 'refresh'
DESCRIPTION = (
    """
    Rewrites the current state of the project to the results directory for
    viewing. Useful when you want to update support files.
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
    """ """

    project = cauldron.project.internal_project
    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is open. Unable to refresh'
        ).console(
            '[ABORTED]: No project is open. Unable to refresh.',
            whitespace=1
        ).response

    try:
        session.initialize_results_path(project.results_path)
        project.write()
    except Exception as err:
        return response.fail(
            code='REFRESH_ERROR',
            message='Unable to refresh project',
            error=err
        ).console(
            whitespace=1
        ).response

    return response.notify(
        kind='SUCCESS',
        code='PROJECT_REFRESHED',
        message='Project notebook display has been refreshed'
    ).console(
        whitespace=1
    ).response
