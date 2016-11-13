#!/usr/bin/env python3

import os
import sys

MY_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


def run():
    try:
        import cauldron
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(MY_DIRECTORY, '..', '..')))

        try:
            import cauldron
        except ImportError:
            raise ImportError(' '.join((
                'Unable to import cauldron.'
                'The package was not installed in a known location.'
            )))

    from cauldron.cli.server import run

    run.execute(**run.parse())


if __name__ == '__main__':
    run()
