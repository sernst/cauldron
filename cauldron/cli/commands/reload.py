import os

import cauldron
from cauldron import cli
from cauldron.cli import sync
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


def execute_remote(context: cli.CommandContext) -> Response:
    """ """

    thread = sync.send_remote_command(
        command=context.name,
        raw_args=context.raw_args,
        asynchronous=False
    )

    thread.join()

    response = thread.responses[0]
    return context.response.consume(response)


def execute(context: cli.CommandContext) -> Response:
    """ """

    response = context.response
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
