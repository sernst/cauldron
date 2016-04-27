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

    project.refresh()
    reporting.initialize_results_path(project.results_path)


    if not target or target[0] == '@all':
        runner.complete(project)
        return

    environ.log('Running step "{}"'.format(target[0]))
    runner.step(project, target[0])
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

        step_names = [x.id for x in cauldron.project.internal_project.steps]
        return autocompletion.matches(segment, *step_names)
