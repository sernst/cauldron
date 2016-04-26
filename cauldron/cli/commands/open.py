import os
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron import runner

DESCRIPTION = """
Opens the specified Cauldron project
"""


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'path',
        type=str,
        help=cli.reformat("""
            Starts the execution
            """)
    )


def execute(parser: ArgumentParser, path: str):
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if path.startswith('::example'):
        parts = path.replace('\\', '/').strip('/').split('/')
        path = environ.paths.package('examples', *parts[1:])
    elif path.startswith('::last'):
        if len(recent_paths) < 1:
            environ.log(
                """
                [ERROR]: No projects have been opened recently
                """
            )
        path = recent_paths[0]

    path = environ.paths.clean(path)
    if not os.path.exists(path):
        environ.log(
            """
            [ERROR]: The specified path does not exist:

            "{path}"

            Unable to start
            """.format(path=path)
        )
        return

    environ.log('Starting: {}'.format(path))

    runner.initialize(path)

    if path in recent_paths:
        recent_paths.remove(path)
    recent_paths.insert(0, path)
    environ.configs.put(recent_paths=recent_paths[:10], persists=True)
    environ.configs.save()

