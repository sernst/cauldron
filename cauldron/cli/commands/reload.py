import os
import typing
from argparse import ArgumentParser

import cauldron
from cauldron import environ
from cauldron import runner
from cauldron import session
from cauldron.environ import Response

NAME = 'reload'
DESCRIPTION = """
    Discards all shared data and reloads the currently open project to its
    initial state
    """


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
    :return:
    """
    pass


def execute(
        parser: ArgumentParser,
        response: Response = None
):

    recent_paths = environ.configs.fetch('recent_paths', [])

    if not recent_paths:
        return

    path = recent_paths[0]
    path = environ.paths.clean(path)
    if not os.path.exists(path):
        environ.log(
            """
            The specified path does not exist:

            "{path}"
            """.format(path=path),
            whitespace=1
        )
        return

    try:
        runner.initialize(path)
    except FileNotFoundError:
        environ.log(
            '[Error]: Project not found',
            whitespace=1
        )
        return

    environ.log(
        '[RELOADED]: {}'.format(path),
        whitespace=1
    )

    project = cauldron.project.internal_project

    if project.results_path:
        session.initialize_results_path(project.results_path)

    path = project.output_path
    if not path or not os.path.exists(path):
        project.write()

