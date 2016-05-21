from argparse import ArgumentParser
import typing
import re

import cauldron
from cauldron import cli
from cauldron.cli import autocompletion
from cauldron import environ
from cauldron import reporting
from cauldron import runner

DESCRIPTION = cli.reformat("""
    Runs one or more steps within the currently opened project
    """)


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'step',
        nargs='*',
        default=None,
        help=cli.reformat("""
            The name of the step, or a space-separated list of steps to be run.
            If this argument is omitted, all steps in the project will be run.
            """)
    )

    parser.add_argument(
        '-f', '--force',
        dest='force',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When this option is included, the step or steps will run even if
            they have not been modified. This is useful when you've updated
            external data or code, but not the project code file(s).
            """)
    )

    parser.add_argument(
        '-c', '--continue',
        dest='continue_after',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When this option is included, all steps after the one specified
            will be run as well as the specified step.
            """)
    )

    parser.add_argument(
        '-s', '--step',
        dest='single_step',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When this option is included, only the first step that needs to be
            updated will be run.
            """)
    )

    parser.add_argument(
        '-l', '--limit',
        dest='limit',
        default=-1,
        type=int,
        help=cli.reformat("""
            The maximum number of steps to run including any specified first
            step. Useful is you want to run only a section of the project.
            """)
    )


def execute(
        parser: ArgumentParser,
        step: list,
        force: bool = False,
        continue_after: bool = False,
        single_step: bool = False,
        limit: int = -1
):
    """

    :param parser:
    :param step:
    :param force:
    :param continue_after:
    :param single_step:
    :param limit:
    :return:
    """

    project = cauldron.project.internal_project

    if not project:
        environ.log(
            """
            [ERROR]: No project has been opened. Use the "open" command to
                open a project.
            """,
            whitespace=1
        )
        return

    was_loaded = bool(project.last_modified is not None)
    if project.refresh() and was_loaded:
        environ.log(
            """
            [WARNING]: The project was reloaded due to changes detected in
                the cauldron.json settings file. Shared data was reset as a
                result.
            """,
            whitespace=1
        )

    reporting.initialize_results_path(project.results_path)

    try:
        # Special cases that apply limits
        if re.match(r'[0-9]+$', step[-1]):
            limit = int(step[-1])
        elif re.match(r'[\.]+', step[-1]):
            limit = len(step[-1])
        step.pop()
    except Exception:
        pass

    project_steps = []
    for s in project.steps:
        if s.id in step:
            project_steps.append(s)

    for ps in project_steps:
        step.remove(ps.id)

    if len(step) > 0:
        message = ['  * "{}"'.format(x) for x in step]
        message.insert(0, '[ABORTED]: Unable to locate the following step(s):')
        environ.log(message, whitespace=1)
        return

    environ.log(
        'RUNNING\n-------',
        whitespace_top=1
    )

    if single_step:
        ps = project_steps[0] if len(project_steps) > 0 else None
        runner.section(project, ps, 1)
    elif continue_after:
        runner.complete(project, project_steps[0], force=force, limit=limit)
        environ.log_blanks()
        return
    elif len(project_steps) == 0:
        runner.complete(project, force=force, limit=limit)
        environ.log_blanks()
        return
    elif limit > 0:
        for ps in project_steps:
            index = project.steps.index(ps)
            for i in range(index, len(project.steps)):
                start = project.steps[index]
                if start.is_dirty():
                    runner.section(project, start, limit)
                    break
    else:
        for ps in project_steps:
            runner.step(project, ps, force=force)

    project.write()
    environ.log_blanks()


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
            shorts=['f', 'c', 's', 'l'],
            longs=['force', 'continue', 'step', 'limit']
        )

    if len(parts) < 1:
        return []

    value = parts[-1]
    project = cauldron.project.internal_project
    step_ids = [x.id for x in project.steps]
    return autocompletion.match_in_path_list(segment, value, step_ids)


