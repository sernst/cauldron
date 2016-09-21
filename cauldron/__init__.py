from cauldron import session as _session
from cauldron.session import display
from cauldron.session.reloading import refresh
from cauldron.session.caching import SharedCache as _SharedCache

project = _session.project  # type: _session.ExposedProject

step = _session.step  # type: _session.ExposedStep

shared = _session.project.shared  # type: _SharedCache


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

    from cauldron.cli.server import run as run_server
    run_server.execute(port, debug, **kwargs)
