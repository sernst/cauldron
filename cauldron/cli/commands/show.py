import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron.environ import Response

NAME = 'show'
DESCRIPTION = 'Opens the current project display in the default browser'


def execute_remote(context: cli.CommandContext) -> Response:
    """ """

    response = sync.comm.send_request(
        endpoint='/status',
        remote_connection=context.remote_connection
    )

    remote_slug = response.data.get('project', {}).get('remote_slug')
    if response.success:
        url = ''.join([
            context.remote_connection.url.rstrip('/'),
            '/',
            remote_slug.lstrip('/')
        ])

        cli.open_in_browser(url)

    return context.response.consume(response)


def execute(context: cli.CommandContext) -> Response:
    """

    :return:
    """

    response = context.response
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
