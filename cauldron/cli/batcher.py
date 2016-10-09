import os
from argparse import ArgumentParser

import cauldron
from cauldron import environ
from cauldron.cli import commander
from cauldron.cli.commands import close as close_command
from cauldron.cli.commands import open as open_command
from cauldron.cli.commands import run as run_command
from cauldron.environ import logger


def initialize_logging_path(path: str = None) -> str:
    """

    :param path:
    :return:
    """

    path = environ.paths.clean(path if path else '.')

    if os.path.isdir(path) and os.path.exists(path):
        path = os.path.join('cauldron_run.log')
    elif os.path.exists(path):
        os.remove(path)

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return path


def run_project(
        project_directory: str,
        output_directory: str = None,
        log_path: str = None
) -> environ.Response:
    log_path = initialize_logging_path(log_path)

    logger.add_output_path(log_path)

    def onComplete(message: str = None) -> environ.Response:
        if message:
            logger.log(message)
        logger.remove_output_path(log_path)
        return response

    response = environ.Response()
    parser = ArgumentParser()

    open_command.execute(
        parser,
        response,
        project_directory,
        results_path=output_directory
    )
    if response.failed:
        return onComplete('[ERROR]: Aborted trying to open project')

    output_directory = cauldron.project.internal_project.results_path

    commander.preload()
    run_command.execute(parser, response)
    if response.failed:
        return onComplete('[ERROR]: Aborted trying to run project steps')

    close_command.execute(parser, response)
    if response.failed:
        return onComplete('[ERROR]: Failed to close project cleanly after run')

    return onComplete('Project execution complete')
