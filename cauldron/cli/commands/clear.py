import cauldron
from cauldron import cli
from cauldron.environ import Response
from cauldron.cli import sync

NAME = 'clear'
DESCRIPTION = """
    Clears all shared data in the cache and reloads all internal project
    libraries.
    """


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
    """

    :return:
    """

    project = cauldron.project.internal_project

    if not project:
        return context.response.fail(
            code='NO_OPEN_PROJECT',
            message='No open project on which to clear data'
        ).console(
            whitespace=1
        ).response

    project.shared.clear()

    for ps in project.steps:
        ps.mark_dirty(True)

    return context.response.update(
        project=project.kernel_serialize()
    ).notify(
        kind='SUCCESS',
        code='SHARED_CLEARED',
        message='Shared data has been cleared'
    ).console(
        whitespace=1
    ).response
