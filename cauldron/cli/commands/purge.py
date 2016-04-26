import os
import shutil
from argparse import ArgumentParser

from cauldron import environ
from cauldron.cli import query

DESCRIPTION = """
    Removes all existing group and trial results from cached results folders
    """


def prepare(parser: ArgumentParser):
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

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception:
            try:
                shutil.rmtree(path)
            except Exception:
                pass

    environ.log("""
        [SUCCESS]: All results have been removed
        """, whitespace_top=1)


