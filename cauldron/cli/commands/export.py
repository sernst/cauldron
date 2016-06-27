from argparse import ArgumentParser
import os
import shutil
import typing

import cauldron
from cauldron import environ
from cauldron import cli

NAME = 'export'
DESCRIPTION = """
    Export the current project's results html file
    """


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    parser.add_argument(
        'path',
        type=str,
        help=cli.reformat("""
            The path where the single html file will be exported
            """)
    )

    parser.add_argument(
        '-d', '--directory',
        dest='directory_name',
        type=str,
        default=None,
        help=cli.reformat("""
            The name of the directory where the results will be exported. If
            omitted, the default will be the identifier for the project.
            """)
    )


def execute(parser: ArgumentParser, path: str, directory_name: str = None):
    """

    :param parser:
    :param path:
    :return:
    """
    results_path = environ.configs.make_path(
        'results', override_key='results_path'
    )

    pid = cauldron.project.internal_project.id

    if directory_name is None:
        directory_name = pid
    out_path = os.path.join(environ.paths.clean(path), directory_name)

    environ.systems.remove(out_path)
    os.makedirs(out_path)

    for item in os.listdir(results_path):
        item_path = os.path.join(results_path, item)
        if not os.path.isfile(item_path):
            continue
        item_out_path = os.path.join(out_path, item)

        shutil.copy2(item_path, item_out_path)

    report_path = os.path.join(results_path, 'reports', pid)
    report_out_path = os.path.join(out_path, 'data')
    shutil.copytree(report_path, report_out_path)

    html_path = os.path.join(out_path, 'project.html')
    with open(html_path, 'r+') as f:
        dom = f.read()

    dom = dom.replace(
        '<!-- CAULDRON:EXPORT -->',
        cli.reformat("""
            <script>
                window.RESULTS_FILENAME = 'data/results.js';
            </script>
            """)
    )

    with open(html_path, 'w+') as f:
        f.write(dom)


