import typing
from argparse import ArgumentParser

from cauldron import environ
from cauldron.cli.interaction import query

NAME = 'purge'
DESCRIPTION = """
    Removes all existing group and trial results from cached results folders
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
    pass


def execute(parser: ArgumentParser):
    """

    :return:
    """

    path = environ.configs.make_path('results', override_key='results_path')
    environ.log("""
        ==============
        REMOVE RESULTS
        ==============

        This command will remove all existing results stored in the directory:

        {path}
        """.format(path=path), whitespace_bottom=1)

    do_it = query.confirm(
        'Are you sure you want to continue',
        default=False
    )

    if not do_it:
        environ.log('[ABORTED]: No files were deleted')
        return

    if environ.systems.remove(path):
        msg = '[SUCCESS]: All results have been removed'
    else:
        msg = '[ERROR]: Failed to remove results directory'

    environ.log(msg, whitespace_top=1)


