import os

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli import commander
from cauldron.cli.commands import close as close_command
from cauldron.cli.commands import open as open_command
from cauldron.cli.commands import run as run_command
from cauldron.cli.commands import save as save_command
from cauldron.environ import logger


def initialize_logging_path(path: str = None) -> str:
    """
    Initializes the logging path for running the project. If no logging path
    is specified, the current directory will be used instead.

    :param path:
        Path to initialize for logging. Can be either a path to a file or
        a path to a directory. If a directory is specified, the log file
        written will be called "cauldron_run.log".
    :return:
        The absolute path to the log file that will be used when this project
        is executed.
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
        log_path: str = None,
        shared_data: dict = None,
        reader_path: str = None
) -> environ.Response:
    """
    Opens, executes and closes a Cauldron project in a single command in
    production mode (non-interactive).

    :param project_directory:
        Directory where the project to run is located
    :param output_directory:
        Directory where the project display data will be saved
    :param log_path:
        Path to a file or directory where logging information will be
        written
    :param shared_data:
        Data to load into the cauldron.shared object prior to executing the
        project
    :param reader_path:
        Specifies a path where a reader file will be saved after the project
        has finished running. If no path is specified, no reader file will be
        saved. If the path is a directory, a reader file will be saved in that
        directory with the project name as the file name.
    :return:
        The response result from the project execution
    """

    log_path = initialize_logging_path(log_path)
    logger.add_output_path(log_path)

    def on_complete(message: str = None) -> environ.Response:
        environ.modes.remove(environ.modes.SINGLE_RUN)
        if message:
            logger.log(message)
        logger.remove_output_path(log_path)
        return response

    environ.modes.add(environ.modes.SINGLE_RUN)

    response = open_command.execute(
        context=cli.make_command_context(open_command.NAME),
        path=project_directory,
        results_path=output_directory
    )
    if response.failed:
        return on_complete('[ERROR]: Aborted trying to open project')

    project = cauldron.project.internal_project
    project.shared.put(**(shared_data if shared_data is not None else dict()))

    commander.preload()
    response = run_command.execute(
        context=cli.make_command_context(run_command.NAME)
    )
    if response.failed:
        return on_complete('[ERROR]: Aborted trying to run project steps')

    if reader_path:
        save_command.execute(
            context=cli.make_command_context(save_command.NAME),
            path=reader_path
        )

    response = close_command.execute(
        context=cli.make_command_context(close_command.NAME)
    )
    if response.failed:
        return on_complete('[ERROR]: Failed to close project cleanly after run')

    return on_complete('Project execution complete')
