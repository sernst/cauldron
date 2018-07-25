import json
import os
import typing
from argparse import ArgumentParser

from cauldron import environ
from cauldron.cli import batcher
from cauldron.cli.shell import CauldronShell
from cauldron.cli.server import run as server_run


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
    """Runs a batch operation for the given arguments"""

    batcher.run_project(
        project_directory=args.get('project_directory'),
        log_path=args.get('logging_path'),
        output_directory=args.get('output_directory'),
        shared_data=load_shared_data(args.get('shared_data_path'))
    )
    return 0


def run_shell(args: dict) -> int:
    """Run the shell sub command"""

    if args.get('project_directory'):
        return run_batch(args)

    shell = CauldronShell()

    if in_project_directory():
        shell.cmdqueue.append('open "{}"'.format(os.path.realpath(os.curdir)))

    shell.cmdloop()
    return 0


def run_kernel(args: dict) -> int:
    """Runs the kernel sub command"""
    server_run.execute(**args)
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
        version=run_version
    )

    if action not in actions:
        print('[ERROR]: Unrecognized sub command "{}"'.format(action))
        parser = args['parser']  # type: ArgumentParser
        parser.print_help()
        return 1

    return actions.get(action)(args)
