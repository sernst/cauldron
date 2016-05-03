import os
import typing
import webbrowser
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron.cli import query
from cauldron.cli import autocompletion
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

    if path.startswith('@examples:'):
        path = path.lstrip(':').split(':', 1)[-1]
        parts = path.replace('\\', '/').strip('/').split('/')
        path = environ.paths.package('examples', *parts)

    elif path.startswith('@last'):
        if len(recent_paths) < 1:
            environ.log(
                """
                No projects have been opened recently
                """
            )
            return
        path = recent_paths[0]

    elif path.startswith('@recent'):
        if len(recent_paths) < 1:
            environ.log(
                """
                There are no recent projects available to open.
                """
            )
            return

        path = query.choice(
            'Recently Opened Projects',
            'Choose a project',
            recent_paths,
            0
        )

    path = environ.paths.clean(path)
    if not os.path.exists(path):
        environ.log(
            """
            The specified path does not exist:

            "{path}"
            """.format(path=path)
        )
        return

    try:
        runner.initialize(path)
    except FileNotFoundError:
        environ.log('Error: Project not found')
        return

    environ.log('Opened: {}'.format(path))

    if path in recent_paths:
        recent_paths.remove(path)
    recent_paths.insert(0, path)
    environ.configs.put(recent_paths=recent_paths[:10], persists=True)
    environ.configs.save()

    url = cauldron.project.internal_project.write()

    environ.log(
        """
        Project URL:
          * {url}
        """.format(url=url)
    )

    webbrowser.open(url)


def autocomplete(segment: str, line:str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    # print('{e}[9999D{e}[KAUTO "{prefix}" {parts}\n>>> {line}'.format(
    #     prefix=segment,
    #     parts=parts,
    #     line=line,
    #     e=chr(27)
    # ), end='')

    if len(parts) == 1:
        value = parts[0]

        if value.startswith('@examples:'):
            segment = value.split(':', 1)[-1]
            return autocompletion.match_path(
                segment,
                environ.paths.package('examples', segment),
                include_files=False
            )

        if value.startswith('@'):
            return autocompletion.matches(
                segment,
                'last',
                'examples:',
                'recent'
            )

        return  autocompletion.match_path(segment, value)
