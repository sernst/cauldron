from cauldron import cli
from cauldron import runner
from cauldron.environ import Response
from cauldron.cli import sync

NAME = 'close'
DESCRIPTION = """
    Close the currently opened project
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
    """ """
    if runner.close():
        return context.response.notify(
            kind='SUCCESS',
            code='PROJECT_CLOSED',
            message='Project has been closed'
        ).console(
            whitespace=1
        ).response

    return context.response.notify(
        kind='ABORTED',
        code='NO_OPEN_PROJECT',
        message='There was no open project to close'
    ).console(
        whitespace=1
    ).response
