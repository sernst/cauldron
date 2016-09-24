import os
import shutil
import typing
import glob
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli.interaction import autocompletion
from cauldron.environ import Response

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
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='When specified, any existing output folder will be overwritten'
    )

    parser.add_argument(
        '-a', '--append',
        dest='append',
        action='store_true',
        default=False,
        help=cli.reformat(
            """
            When specified, the export will be appended to any
            existing exports
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


def execute(
        parser: ArgumentParser,
        response: Response,
        path: str,
        directory_name: str = None,
        force: bool = False,
        append: bool = False
) -> Response:
    """

    :param parser:
    :param response:
    :param path:
    :param directory_name:
    :param force:
    :param append:
    :return:
    """

    if path is None:
        return response.fail(
            code='MISSING_PATH_ARG',
            message='Missing export path argument'
        ).console(
            whitespace=1
        ).response

    path = path.strip('"')
    directory_name = directory_name.strip('"') if directory_name else None

    project = cauldron.project.internal_project
    results_path = project.results_path
    pid = cauldron.project.internal_project.id

    if directory_name is None:
        directory_name = pid
    out_path = os.path.join(environ.paths.clean(path), directory_name)

    if force:
        environ.systems.remove(out_path)

    exists = os.path.exists(out_path)

    if not append and exists:
        return response.fail(
            code='ALREADY_EXISTS',
            message='Export directory already exists'
        ).console(
            whitespace=1
        ).response

    if append and exists:
        append_to_existing_export(results_path, out_path)
    else:
        shutil.copytree(results_path, out_path)

    html_path = os.path.join(out_path, 'project.html')
    with open(html_path, 'r+') as f:
        dom = f.read()

    dom = dom.replace(
        '<!-- CAULDRON:EXPORT -->',
        cli.reformat(
            """
            <script>
                window.RESULTS_FILENAME = 'reports/{uuid}/latest/results.js';
                window.PROJECT_ID = '{uuid}';
            </script>
            """.format(uuid=project.uuid)
        )
    )

    html_out_path = os.path.join(out_path, '{}.html'.format(pid))
    with open(html_out_path, 'w+') as f:
        f.write(dom)

    environ.systems.remove(html_path)
    return response


def append_to_existing_export(source_directory, output_directory):
    """

    :param source_directory:
    :param output_directory:
    :return:
    """

    path_glob = glob.iglob(
        os.path.join(source_directory, '**', '*'),
        recursive=True
    )

    for src_path in path_glob:
        partial = src_path[len(source_directory):].lstrip(os.sep)
        out_path = os.path.join(output_directory, partial)

        if os.path.isdir(src_path):
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            continue

        if os.path.exists(out_path):
            environ.systems.remove(out_path)
        shutil.copy2(src_path, out_path)


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if parts[-1].startswith('-'):
        return autocompletion.match_flags(
            segment=segment,
            value=parts[-1],
            shorts=['f', 'a', 'd'],
            longs=['force', 'append', 'directory']
        )

    if len(parts) == 1:
        return autocompletion.match_path(segment, parts[0])

    return []
