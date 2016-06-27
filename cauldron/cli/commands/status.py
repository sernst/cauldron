from argparse import ArgumentParser

import cauldron
from cauldron import environ

NAME = 'status'
DESCRIPTION = """
    Displays the status of project and the shared workspace variables
    """


def execute(parser: ArgumentParser):

    project = cauldron.project.internal_project

    data = project.shared.fetch(None)
    keys = list(data.keys())
    keys.sort()

    for k in keys:

        if k.startswith('__cauldron_'):
            continue

        try:
            data_type = data[k].__class__.__name__
        except Exception:
            data_type = type(data[k])

        value = '{}'.format(data[k])[:250].replace('\n', '\n   ')
        if value.find('\n') != -1:
            value = '\n{}'.format(value)

        environ.log(
            """
            + {name} ({type}): {value}
            """.format(
                name=k,
                type=data_type,
                value=value
            ),
            whitespace_bottom=1
        )
