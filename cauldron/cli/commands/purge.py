import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron.cli import sync
from cauldron import environ
from cauldron.cli.interaction import query
from cauldron.environ import Response

NAME = 'purge'
DESCRIPTION = 'Removes all results files from Cauldron\'s cache'

ALL_MESSAGE = cli.reformat(
    """
    This command will remove the cached display files for all projects
    in the currently active results directory
    """
)

PROJECT_MESSAGE = cli.reformat(
    """
    This command will remove the cached display files for the currently
    opened project
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
        '-f', '--force',
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
            instead of just for a specific project
            """
        )
    )


def remote_purge(context: cli.CommandContext) -> Response:
    """ """

    thread = sync.send_remote_command(
        command=context.name,
        raw_args='{} --force'.format(context.raw_args),
        asynchronous=False
    )

    thread.join()

    response = thread.responses[0]
    return context.response.consume(response)


def execute(
        context: cli.CommandContext,
        force: bool = False,
        all_projects: bool = False
) -> Response:
    """

    :param context:
    :param force:
    :param all_projects:
    """

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
        ).console(
            whitespace=1
        ).response

    if context.remote_connection.active:
        return remote_purge(context)

    path = environ.configs.fetch('results_directory')
    path = path if path else environ.paths.user('results')

    if environ.systems.remove(path):
        response.notify(
            kind='SUCCESS',
            code='RESULTS_PURGED',
            message='All results have been removed'
        ).console(
            whitespace=1
        )
    else:
        response.fail(
            code='PURGE_FAILURE',
            message='Failed to remove results'
        ).console(
            whitespace=1
        )

    return response
