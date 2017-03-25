import cauldron
from cauldron import session
from cauldron.environ import Response
from cauldron.session.projects import Project


def get_project(response: Response):
    """

    :return:
    """

    project = cauldron.project.internal_project

    if not project:
        response.fail(
            code='NO_OPEN_PROJECT',
            message='No project opened'
        ).console(
            """
            [ERROR]: No project has been opened. Use the "open" command to
                open a project, or the "create" command to create a new one.
            """,
            whitespace=1
        )
        return None

    return project


def preload_project(response: Response, project: Project):
    """

    :param response:
    :param project:
    :return:
    """

    session.initialize_results_path(project.results_path)
