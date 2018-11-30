import re
import typing
from argparse import ArgumentParser
from collections import OrderedDict

import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron import environ
from cauldron import runner
from cauldron.cli.commands.run import actions as run_actions
from cauldron.cli.commands import sync as sync_command
from cauldron.cli.interaction import autocompletion
from cauldron.session import writing
from cauldron.environ import Response
from cauldron.session import projects

NAME = 'run'
DESCRIPTION = cli.reformat(
    """
    Runs one or more steps within the currently opened project
    """
)


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
        '--skip-reload',
        dest='skip_library_reload',
        default=False,
        action='store_true',
        help=cli.reformat("""
            Whether or not to skip reloading all project libraries prior to
            execution of the project. By default this is False in which case 
            the project libraries are reloaded prior to execution.
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

    parser.add_argument(
        '-ps', '--print-status',
        dest='print_status',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            Whether or not to print detailed status after the run command
            completes
            """
        )
    )


def execute_remote(context: cli.CommandContext, **kwargs) -> Response:
    """ """

    sync_response = sync_command.execute(cli.make_command_context(
        name=sync_command.NAME,
        remote_connection=context.remote_connection
    ))
    context.response.consume(sync_response)

    if sync_response.failed:
        return context.response

    environ.log('[STARTED]: Remote run execution', whitespace=1)

    thread = sync.send_remote_command(
        command=context.name,
        raw_args=context.raw_args,
        asynchronous=True,
        show_logs=True
    )

    thread.join()

    response = thread.responses[-1]
    return context.response.consume(response)


def execute(
        context: cli.CommandContext,
        step: list = None,
        force: bool = False,
        continue_after: bool = False,
        single_step: bool = False,
        limit: int = -1,
        print_status: bool = False,
        skip_library_reload: bool = False
) -> Response:
    """

    :param context:
    :param step:
    :param force:
    :param continue_after:
    :param single_step:
    :param limit:
    :param print_status:
    :param skip_library_reload:
        Whether or not to skip reloading all project libraries prior to
        execution of the project. By default this is False in which case
        the project libraries are reloaded prior to execution.
    :return:
    """
    project = run_actions.get_project(context.response)
    if not project:
        return context.response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is open. Unable to execute run command.'
        ).console(
            whitespace=1
        ).response

    run_actions.preload_project(context.response, project)

    steps = list(step) if step else []
    steps = list(OrderedDict.fromkeys([s.strip('"') for s in steps]).keys())

    try:
        # Special cases that apply limits
        if re.match(r'[0-9]+$', steps[-1]):
            limit = int(steps[-1])
            steps.pop()
        elif re.match(r'[\.]+$', steps[-1]):
            limit = len(steps[-1])
            steps.pop()
    except Exception:
        pass

    project_steps = [project.get_step(name) for name in steps]

    if None in project_steps:
        missing_steps = [
            steps[index] for index, value in enumerate(project_steps)
            if value is None
        ]
        message = ['  * "{}"'.format(x) for x in missing_steps]
        message.insert(0, '[ABORTED]: Unable to locate the following step(s):')
        return context.response.fail(
            code='MISSING_STEP',
            message='Unable to locate steps'
        ).kernel(
            steps=[x for x in steps]
        ).console(
            message,
            whitespace=1
        ).response

    return run_local(
        context=context,
        project=project,
        project_steps=project_steps,
        force=force,
        continue_after=continue_after,
        single_step=single_step,
        limit=limit,
        print_status=print_status,
        skip_library_reload=skip_library_reload
    )


def run_local(
        context: cli.CommandContext,
        project: projects.Project,
        project_steps: typing.List[projects.ProjectStep],
        force: bool,
        continue_after: bool,
        single_step: bool,
        limit: int,
        print_status: bool,
        skip_library_reload: bool = False
) -> environ.Response:
    """
    Execute the run command locally within this cauldron environment

    :param context:
    :param project:
    :param project_steps:
    :param force:
    :param continue_after:
    :param single_step:
    :param limit:
    :param print_status:
    :param skip_library_reload:
        Whether or not to skip reloading all project libraries prior to
        execution of the project. By default this is False in which case
        the project libraries are reloaded prior to execution.
    :return:
    """
    skip_reload = (
        skip_library_reload
        or environ.modes.has(environ.modes.TESTING)
    )
    if not skip_reload:
        runner.reload_libraries()

    environ.log_header('RUNNING', 5)

    steps_run = []

    if single_step:
        # If the user specifies the single step flag, only run one step. Force
        # the step to be run if they specified it explicitly

        ps = project_steps[0] if len(project_steps) > 0 else None
        force = force or (single_step and bool(ps is not None))
        steps_run = runner.section(
            response=context.response,
            project=project,
            starting=ps,
            limit=1,
            force=force
        )

    elif continue_after or len(project_steps) == 0:
        # If the continue after flag is set, start with the specified step
        # and run the rest of the project after that. Or, if no steps were
        # specified, run the entire project with the specified flags.

        ps = project_steps[0] if len(project_steps) > 0 else None
        steps_run = runner.complete(
            context.response,
            project,
            ps,
            force=force,
            limit=limit
        )
    else:
        for ps in project_steps:
            steps_run += runner.section(
                response=context.response,
                project=project,
                starting=ps,
                limit=max(1, limit),
                force=force or (limit < 1 and len(project_steps) < 2),
                skips=steps_run + []
            )

    project.write()
    environ.log_blanks()

    step_changes = []
    for ps in steps_run:
        step_changes.append(dict(
            name=ps.definition.name,
            action='updated',
            step=writing.step_writer.serialize(ps)._asdict()
        ))

    context.response.update(step_changes=step_changes)

    if print_status or context.response.failed:
        context.response.update(project=project.kernel_serialize())

    return context.response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if len(parts) < 1:
        return []

    if parts[-1].startswith('-'):
        return autocompletion.match_flags(
            segment=segment,
            value=parts[-1],
            shorts=['f', 'c', 's', 'l'],
            longs=['force', 'continue', 'step', 'limit', 'skip-reload']
        )

    value = parts[-1]
    project = cauldron.project.internal_project
    step_names = [x.definition.name for x in project.steps]
    return autocompletion.match_in_path_list(segment, value, step_names)



