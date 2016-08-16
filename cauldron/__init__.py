from cauldron import session
from cauldron.session import display

project = session.project

shared = session.project.shared


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
