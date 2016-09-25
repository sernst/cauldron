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
    """
    Starts the cauldron shell environment for console based interaction
    :return:
    """

    from cauldron.cli.shell import CauldronShell
    CauldronShell().cmdloop()


def run_server(port=5010, debug=False, **kwargs):
    """
    Run the cauldron http server used to interact with cauldron from a remote
    host

    :param port:
        The port on which to bind the cauldron server
    :param debug:
        Whether or not the server should be run in debug mode. If true, the
        server will echo debugging information during operation.
    :param kwargs:
    :return:
    """

    from cauldron.cli.server import run as server_runner
    server_runner.execute(port, debug, **kwargs)
