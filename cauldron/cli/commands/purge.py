import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli import sync
from cauldron.cli.commands.open import opener
from cauldron.cli.interaction import query
from cauldron.environ import Response

NAME = 'purge'
DESCRIPTION = (
    """
    Removes notebook display files from Cauldron cache for the currently
    open project or all projects if so desired.
    """
)

ALL_MESSAGE = cli.reformat(
    """
    This command will remove the cached display files for all projects
    in the currently active results directory.
    """
)

PROJECT_MESSAGE = cli.reformat(
    """
    This command will remove the cached display files for the currently
    opened project.
    """
)


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """..."""
    parser.add_argument(
        '-y', '--yes',
        dest='force',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            When this option is included, the purge operation will happen
            without an interactive confirmation step
            """
        )
    )

    parser.add_argument(
        '-a', '--all',
        dest='all_projects',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            When this option is included, the purge operation be carried out
            for all projects that store results in the current results directory
            instead of just for a specific project.
            """
        )
    )


def _remote_purge(context: cli.CommandContext) -> Response:
    """..."""
    thread = sync.send_remote_command(
        command=context.name,
        raw_args='{} --yes'.format(context.raw_args),
        asynchronous=False
    )

    thread.join()

    response = thread.responses[0]
    return context.response.consume(response)


def _purge_project(context: cli.CommandContext) -> Response:
    """..."""
    project = cauldron.project.get_internal_project(0.5)
    if not project:
        return context.response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is opened on which to purge.'
        )

    if not environ.systems.remove(project.results_path):
        return context.response.fail(
            code='UNABLE_TO_REMOVE',
            message='Failed to purge project display files.'
        ).console(whitespace=1).response

    # After purging the results, a new results folder should
    # be created and populated with skeletons of the new results
    # files. The step doms are also emptied so that they don't
    # just end up rewriting the existing issue.
    opener.initialize_results(context.response, project)
    for step in project.steps:
        step.clear_dom()
    project.write()
    return context.response.notify(
        kind='SUCCESS',
        code='PROJECT_RESULTS_PURGED',
        message='Project results files have been removed.'
    ).console(whitespace=1).response


def _purge_all(context: cli.CommandContext) -> Response:
    """..."""
    path = environ.configs.fetch('results_directory')
    path = path if path else environ.paths.user('results')

    if environ.systems.remove(path):
        return context.response.notify(
            kind='SUCCESS',
            code='RESULTS_PURGED',
            message='All results have been removed'
        ).console(whitespace=1).response

    return context.response.fail(
        code='PURGE_FAILURE',
        message='Failed to remove results'
    ).console(whitespace=1).response


def execute(
        context: cli.CommandContext,
        force: bool = False,
        all_projects: bool = False
) -> Response:
    """..."""
    response = context.response
    environ.log_header('REMOVE RESULTS', level=2)
    environ.log(
        ALL_MESSAGE if all_projects else PROJECT_MESSAGE,
        whitespace=1
    )

    do_it = force
    if not force:
        do_it = query.confirm(
            'Are you sure you want to continue',
            default=False
        )

    if not do_it:
        return response.notify(
            kind='ABORTED',
            code='NO_PURGE',
            message='No files were deleted'
        ).console(whitespace=1).response

    if context.remote_connection.active:
        return _remote_purge(context)

    if all_projects:
        return _purge_all(context)

    return _purge_project(context)
