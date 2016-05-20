import webbrowser
from argparse import ArgumentParser

import cauldron
from cauldron import environ

DESCRIPTION = """
    Opens the current project display in the default browser
    """


def prepare(parser: ArgumentParser):
    pass


def execute(parser: ArgumentParser):
    """

    :return:
    """

    project = cauldron.project
    if not project or not project.internal_project.url:
        environ.log(
            """
            [ABORTED]: No project is currently open. Please use the open
                command to load a project.
            """,
            whitespace=1
        )
        return

    webbrowser.open(project.internal_project.url)




