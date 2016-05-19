from argparse import ArgumentParser
import typing

import cauldron
from cauldron.cli import autocompletion
from cauldron import environ
from cauldron import reporting
from cauldron import runner

DESCRIPTION = """
    Runs part or all of the currently started reporting
    """


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'target',
        nargs='*',
        default=None,
        help="""
            What you want to be run. If blank it will run everything
            """
    )


def execute(parser: ArgumentParser, target: list):

    project = cauldron.project.internal_project

    if not project:
        environ.log(
            """
            [ERROR]: No project has been opened. Use the "open" command to
            open a project.
            """
        )
        return

    was_loaded = bool(project.last_modified is not None)
    if project.refresh() and was_loaded:
        environ.log(
            """
            [WARNING]: The project was reloaded due to changes detected in the
            cauldron.json
            """, whitespace=1)

    reporting.initialize_results_path(project.results_path)

    if not target or target[0] == '@all':
        runner.complete(project)
        return

    if not runner.step(project, target[0]):
        environ.log('No such step "{}"'.format(target[0]))
        return

    project.write()


def autocomplete(segment: str, line: str, parts: typing.List[str]):
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

    if len(parts) < 2:

        if len(parts) > 0:
            value = parts[0]

            if value.startswith('@'):
                return autocompletion.matches(
                    segment,
                    'all'
                )

            project = cauldron.project.internal_project
            step_ids = [x.id for x in project.steps]
            return autocompletion.match_in_path_list(segment, value, step_ids)

    return []
