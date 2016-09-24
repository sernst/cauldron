from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.environ import Response

NAME = 'show'
DESCRIPTION = 'Opens the current project display in the default browser'


def execute(
        parser: ArgumentParser,
        response: Response
) -> Response:
    """

    :return:
    """

    project = cauldron.project.internal_project
    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is currently open.'
        ).console(
            """
            [ABORTED]: No project is currently open. Please use the open
                command to load a project.
            """,
            whitespace=1
        ).response

    cli.open_in_browser(project)
    return response
