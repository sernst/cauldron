import cauldron
from cauldron import environ
from cauldron import session
from cauldron.session.projects import Project
from cauldron.environ import Response


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

    was_loaded = bool(project.last_modified is not None)
    if project.refresh() and was_loaded:
        response.notify(
            kind='WARNING',
            code='PROJECT_RELOADED',
            message="""
                The project was reloaded due to changes detected in
                the cauldron.json settings file. Shared data was reset as a
                result.
                """
        ).console(
            whitespace=1
        )

    session.initialize_results_path(project.results_path)
