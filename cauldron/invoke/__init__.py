import typing
import os
import sys
from importlib import import_module

MY_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
ROOT_DIRECTORY = os.path.abspath(os.path.join(MY_DIRECTORY, '..', '..'))


def get_cauldron_module():
    """
    Returns the cauldron module loaded from the import library, or None if
    the Cauldron module could not be loaded.
    """

    try:
        return import_module('cauldron')
    except Exception:
        return None


def initialize():
    """
    Initializes the cauldron library by confirming that it can be imported
    by the importlib library. If the attempt to import it fails, the system
    path will be modified and the attempt retried. If both attempts fail, an
    import error will be raised.
    """

    cauldron_module = get_cauldron_module()
    if cauldron_module is not None:
        return cauldron_module

    sys.path.append(ROOT_DIRECTORY)
    cauldron_module = get_cauldron_module()

    if cauldron_module is not None:
        return cauldron_module

    raise ImportError(' '.join((
        'Unable to import cauldron.'
        'The package was not installed in a known location.'
    )))


def run(arguments: typing.List[str] = None):
    """Executes the cauldron command"""
    initialize()

    from cauldron.invoke import parser
    from cauldron.invoke import invoker

    args = parser.parse(arguments)
    exit_code = invoker.run(args.get('command'), args)
    sys.exit(exit_code)
