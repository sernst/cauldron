import json
import os
import typing
from argparse import ArgumentParser  # noqa

from cauldron import environ
from cauldron import ui
from cauldron.cli import batcher
from cauldron.cli.server import run as server_run
from cauldron.cli.shell import CauldronShell
from cauldron.invoke import containerized


def _pre_run_updater():
    """
    Execute update operations prior to starting the desired process
    action. These operations are used to ensure that the host environment
    is readied for use.
    """
    if environ.configs.fetch('last_version', '0.0.0').startswith('1'):
        return

    # Remove old results as they will cause issues
    environ.systems.remove(environ.paths.results())

    environ.configs.put(persists=True, last_version=environ.version)


def in_project_directory() -> bool:
    """
    Returns whether or not the current working directory is a Cauldron project
    directory, which contains a cauldron.json file.
    """
    current_directory = os.path.realpath(os.curdir)
    project_path = os.path.join(current_directory, 'cauldron.json')
    return os.path.exists(project_path) and os.path.isfile(project_path)


def load_shared_data(path: typing.Union[str, None]) -> dict:
    """Load shared data from a JSON file stored on disk"""

    if path is None:
        return dict()

    if not os.path.exists(path):
        raise FileNotFoundError('No such shared data file "{}"'.format(path))

    try:
        with open(path, 'r') as fp:
            data = json.load(fp)
    except Exception:
        raise IOError('Unable to read shared data file "{}"'.format(path))

    if not isinstance(data, dict):
        raise ValueError('Shared data must load into a dictionary object')

    return data


def run_version(args: dict) -> int:
    """Displays the current version"""
    version = environ.package_settings.get('version', 'unknown')
    print('VERSION: {}'.format(version))
    return 0


def run_batch(args: dict) -> int:
    """Runs a batch operation for the given arguments."""
    batcher.run_project(
        project_directory=args.get('project_directory'),
        log_path=args.get('logging_path'),
        output_directory=args.get('output_directory'),
        shared_data=load_shared_data(args.get('shared_data_path'))
    )
    return 0


def run_shell(args: dict) -> int:
    """Run the shell sub command."""
    _pre_run_updater()
    if args.get('project_directory'):
        return run_batch(args)

    shell = CauldronShell()

    if in_project_directory():
        shell.cmdqueue.append('open "{}"'.format(os.path.realpath(os.curdir)))

    shell.cmdloop()
    return 0


def run_kernel(args: dict) -> int:
    """Runs the kernel sub command"""
    _pre_run_updater()
    server_run.execute(**args)
    return 0


def run_ui(args: dict) -> int:
    """Runs the ui sub command"""
    _pre_run_updater()
    ui.start(**args)
    return 0


def run_view(args: dict) -> int:
    """Runs the view sub command."""
    _pre_run_updater()
    shell = CauldronShell()
    shell.default('view open "{}"'.format(args['path']))
    return 0


def run(action: str, args: dict) -> int:
    """
    Runs the specified command action and returns the return status code
    for exit.

    :param action:
        The action to run
    :param args:
        The arguments parsed for the specified action
    """
    if args.get('show_version_info'):
        return run_version(args)

    actions = dict(
        shell=run_shell,
        kernel=run_kernel,
        serve=run_kernel,
        version=run_version,
        ui=run_ui,
        uidocker=containerized.run_ui,
        view=run_view,
    )

    if action not in actions:
        print('[ERROR]: Unrecognized sub command "{}"'.format(action))
        parser = args['parser']  # type: ArgumentParser
        parser.print_help()
        return 1

    return actions.get(action)(args)
