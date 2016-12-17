#!/usr/bin/env python3

import json
import typing
import os
import sys
from argparse import ArgumentParser


MY_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


def load_shared_data(path: typing.Union[str, None]) -> dict:
    """
    Load shared data from a JSON file stored on disk

    :param path:
    :return:
    """

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


def parse_args():
    parser = ArgumentParser(description='Cauldron')

    parser.add_argument(
        '-v', '--version',
        dest='version',
        default=False,
        action='store_true'
    )

    parser.add_argument(
        '-p', '--project',
        dest='project_directory',
        type=str,
        default=None
    )

    parser.add_argument(
        '-l', '--log',
        dest='logging_path',
        type=str,
        default=None
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_directory',
        type=str,
        default=None
    )

    parser.add_argument(
        '-s', '--shared',
        dest='shared_data_path',
        type=str,
        default=None
    )

    return parser.parse_args()


def run():
    try:
        import cauldron
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(MY_DIRECTORY, '..', '..')))

        try:
            import cauldron
        except ImportError:
            raise ImportError(' '.join((
                'Unable to import cauldron.'
                'The package was not installed in a known location.'
            )))

    from cauldron.cli.shell import CauldronShell
    from cauldron import environ
    from cauldron.cli import batcher

    args = parse_args()

    if args.version:
        print('VERSION: {}'.format(environ.package_settings().get('version', 'unknown')))
        sys.exit(0)

    if args.project_directory:
        batcher.run_project(
            project_directory=args.project_directory,
            log_path=args.logging_path,
            output_directory=args.output_directory,
            shared_data=load_shared_data(args.shared_data_path)
        )
        sys.exit(0)

    CauldronShell().cmdloop()


if __name__ == '__main__':
    run()
