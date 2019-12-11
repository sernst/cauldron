from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.listing import _utils
from cauldron.session.projects import specio


def execute_list(context: cli.CommandContext) -> environ.Response:
    """
    Executes the list action for the recent command according to the
    specified context object for the currently invoked command and
    returns a response object containing the listed projects.
    """
    projects = _utils.get_recent_projects()
    if projects.specs:
        display = 'Recent Projects:\n\n{}'.format(
            specio.to_display_list(projects.specs)
        )
    else:
        display = 'No recent projects found.'

    return (
        context.response
        .update(projects=projects.specs)
        .notify(
            kind='RESULT',
            code='PROJECT_HISTORY',
            message=display
        )
        .console(whitespace=1)
        .response
    )
