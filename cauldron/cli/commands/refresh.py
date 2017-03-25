import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron import session
from cauldron.environ import Response

NAME = 'refresh'
DESCRIPTION = (
    """
    Rewrites the current state of the project to the results directory for
    viewing. Useful when you want to update support files.
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
