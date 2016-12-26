from cauldron import session as _session
from cauldron.session import display as _display
from cauldron.session.reloading import refresh as _refresh
from cauldron.session.caching import SharedCache as _SharedCache
from cauldron.session import spark as _spark
from cauldron import environ as _environ

# Version Information in commonly viewed formats
__version__ = _environ.version  # type: str
version = _environ.version  # type: str
version_info = _environ.version_info  # type: _environ.VersionInfo

project = _session.project  # type: _session.ExposedProject
step = _session.step  # type: _session.ExposedStep
shared = _session.project.shared  # type: _SharedCache

display = _display
refresh = _refresh
mode = _environ.modes.ExposedModes
spark = _spark


def get_environment_info() -> dict:
    """
    Information about Cauldron and its Python interpreter

    :return:
        A dictionary containing information about the Cauldron and its
        Python environment. This information is useful when providing feedback
        and bug reports
    """

    data = _environ.systems.get_system_data()
    data['cauldron'] = _environ.package_settings.copy()
    return data


def run_shell():
    """ Starts the cauldron shell environment for console based interaction """

    from cauldron.cli.shell import CauldronShell
    CauldronShell().cmdloop()


def run_server(port=5010, debug=False, **kwargs):
    """
    Run the cauldron http server used to interact with cauldron from a remote
    host

    :param port:
        The port on which to bind the cauldron server.
    :param debug:
        Whether or not the server should be run in debug mode. If true, the
        server will echo debugging information during operation.
    :param kwargs:
        Custom properties to alter the way the server runs.
    """

    from cauldron.cli.server import run
    run.execute(port=port, debug=debug, **kwargs)


def run_project(
        project_directory: str,
        output_directory: str = None,
        logging_path: str = None,
        **kwargs
) -> _environ.Response:
    """
    Runs a project as a single command directly within the current Python
    interpreter.

    :param project_directory:
        The fully-qualified path to the directory where the Cauldron project is
        located
    :param output_directory:
        The fully-qualified path to the directory where the results will be
        written. All of the results files will be written within this
        directory. If the directory does not exist, it will be created.
    :param logging_path:
        The fully-qualified path to a file that will be used for logging. If a
        directory is specified instead of a file, a file will be created using
        the default filename of cauldron_run.log. If a file already exists at
        that location it will be removed and a new file created in its place.
    :param kwargs:
        Any variables to be available in the cauldron.shared object during
        execution of the project can be specified here as keyword arguments.
    :return:
        A response object that contains information about the run process
    """

    from cauldron.cli import batcher
    return batcher.run_project(
        project_directory=project_directory,
        output_directory=output_directory,
        log_path=logging_path,
        shared_data=kwargs
    )
