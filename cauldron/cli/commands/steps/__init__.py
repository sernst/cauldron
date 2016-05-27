import typing
from argparse import ArgumentParser

import cauldron
from cauldron import environ
from cauldron import cli
from cauldron.cli import autocompletion
from cauldron.cli.commands.steps import actions

DESCRIPTION = """
    Carry out an action on one or more steps within the currently opened
    project.
    """


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'action',
        nargs='*',
        default=None,
        help=cli.reformat("""
            The action that will be carried out on the step(s) within the
            current project. Available actions include:

                - add: Creates a new command with the specified name
                    <>: steps add [STEP_FILE_NAME]

                -list: Lists the steps within the currently opened project
            """)
    )


def execute(
        parser: ArgumentParser,
        action: list,
):
    """

    :return:
    """

    if not cauldron.project or not cauldron.project.internal_project:
        environ.log(
            """
            [ERROR]: No project is currently open. Steps commands only work
                with an open project.
            """,
            whitespace=1
        )
        return

    if not action:
        actions.echo_steps()
        return

    if action[0] == 'add':
        if len(action) < 2:
            environ.log(
                """
                [ABORTED]: Unable to add a new step. A filename for the step
                    is required.
                """,
                whitespace=1
            )
            return

        step_id = actions.create_step(action[1])

        environ.log(
            """
            [CREATED]: "{}" step has been created.
            """.format(step_id),
            whitespace=1
        )
        return

    if action[0] == 'list':
        actions.echo_steps()


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if len(parts) < 2:
        return autocompletion.matches(
            segment,
            parts[0],
            ['add', 'list']
        )

    return []


