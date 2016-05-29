import cauldron
from cauldron import environ
from cauldron.session.project import Project
from cauldron import reporting

def get_project():
    """

    :return:
    """

    project = cauldron.project.internal_project

    if not project:
        environ.log(
            """
            [ERROR]: No project has been opened. Use the "open" command to
                open a project, or the "create" command to create a new one.
            """,
            whitespace=1
        )
        return None

    return project


def preload_project(project: Project):
    """

    :param project:
    :return:
    """

    was_loaded = bool(project.last_modified is not None)
    if project.refresh() and was_loaded:
        environ.log(
            """
            [WARNING]: The project was reloaded due to changes detected in
                the cauldron.json settings file. Shared data was reset as a
                result.
            """,
            whitespace=1
        )

    reporting.initialize_results_path(project.results_path)
