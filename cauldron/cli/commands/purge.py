import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.interaction import query
from cauldron.environ import Response

NAME = 'purge'
DESCRIPTION = 'Removes all results files from Cauldron\'s cache'


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
        help=cli.reformat("""
            When this option is included, the purge operation will happen
            without an interactive confirmation step
            """
        )
    )


def execute(
        parser: ArgumentParser,
        response: Response,
        force: bool = False
) -> Response:
    """

    :param parser:
    :param response:
    :param force:
    :return:
    """

    path = environ.configs.fetch('results_directory')
    if not path:
        path = environ.paths.user('results')

    environ.log("""
        ==============
        REMOVE RESULTS
        ==============

        This command will remove all existing results stored in the directory:

        {path}
        """.format(path=path), whitespace_bottom=1)

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

    if environ.systems.remove(path):
        msg = response.notify(
            kind='SUCCESS',
            code='RESULTS_PURGED',
            message='All results have been removed'
        )
    else:
        msg = response.fail(
            code='PURGE_FAILURE',
            message='Failed to remove results directory'
        )

    return msg.console(whitespace=1).response
