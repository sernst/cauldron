import sys
import traceback
from argparse import ArgumentParser

import cauldron
from cauldron import environ
from cauldron import reporting
from cauldron import runner

DESCRIPTION = """
    Runs part or all of the currently started reporting
    """


def prepare(parser: ArgumentParser):
    pass


def execute(parser: ArgumentParser):

    project = cauldron.project.internal_project

    if not project:
        environ.log(
            """
            [ERROR]: No project has been opened. Use the "open" command to
            open a project.
            """
        )
        return

    project.refresh()
    reporting.initialize_results_path(project.results_path)
    url = runner.complete(project)
    if not url:
        return

    environ.log(
        """
        Report Available at:

         * {url}
        """.format(url=url)
    )
