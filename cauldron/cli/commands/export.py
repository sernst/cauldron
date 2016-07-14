import os
import shutil
import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron import session

NAME = 'export'
DESCRIPTION = 'Export the current project\'s results html file'


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
        default=None,
        help=cli.reformat(
            """
            The path where the single html file will be exported
            """
        )
    )

    parser.add_argument(
        '-d', '--directory',
        dest='directory_name',
        type=str,
        default=None,
        help=cli.reformat(
            """
            The name of the directory where the results will be exported. If
            omitted, the default will be the identifier for the project.
            """
        )
    )


def execute(parser: ArgumentParser, path: str, directory_name: str = None):
    """

    :param parser:
    :param path:
    :param directory_name:
    :return:
    """

    if path is None:
        return environ.output.fail().notify(
            kind='ERROR',
            code='MISSING_PATH_ARG',
            message='Missing export path argument'
        ).console(whitespace=1)

    path = path.strip('"')
    directory_name = directory_name.strip('"') if directory_name else None

    project = cauldron.project.internal_project
    results_path = project.results_path
    pid = cauldron.project.internal_project.id

    if directory_name is None:
        directory_name = pid
    out_path = os.path.join(environ.paths.clean(path), directory_name)

    environ.systems.remove(out_path)
    session.initialize_results_path(out_path)

    report_path = os.path.join(results_path, 'reports', pid)
    report_out_path = os.path.join(out_path, 'reports', pid)
    shutil.copytree(report_path, report_out_path)

    html_path = os.path.join(out_path, 'project.html')
    with open(html_path, 'r+') as f:
        dom = f.read()

    dom = dom.replace(
        '<!-- CAULDRON:EXPORT -->',
        cli.reformat(
            """
            <script>
                window.RESULTS_FILENAME = 'reports/{}/latest/results.js';
            </script>
            """.format(pid)
        )
    )

    with open(html_path, 'w+') as f:
        f.write(dom)


