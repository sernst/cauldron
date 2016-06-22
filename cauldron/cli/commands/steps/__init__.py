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

                - list: Lists the steps within the currently opened project

                - modify: Modifies the specified step. See the flags for
                    modification options
                    <>: steps modify [CURRENT_STEP_NAME]

                - remove: Removes the specified step from the project. The
                    source file will be remove along with the step unless the
                    --keep flag is specified
            """)
    )

    parser.add_argument(
        '-p', '--position',
        dest='position',
        type=str,
        default=None,
        help=cli.reformat(
            """
            Only valid for the add action, this specifies the index where the
            step will be inserted, or the name of the step after which this new
            step will be inserted.
            """
        )
    )

    parser.add_argument(
        '-t', '--title',
        dest='title',
        type=str,
        default=None,
        help=cli.reformat(
            """
            This specifies the title for the step that will be added or
            modified
            """
        )
    )

    parser.add_argument(
        '-n', '--name',
        dest='new_name',
        type=str,
        default=None,
        help=cli.reformat(
            """
            This new name for the step when modifying an existing one
            """
        )
    )

    parser.add_argument(
        '-k', '--keep',
        dest='keep',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            Whether or not to keep the source file when removing a step from
            a project
            """
        )
    )


def execute(
        parser: ArgumentParser,
        action: list,
        position: str = None,
        title: str = None,
        new_name: str = None,
        keep: bool = False
):
    """

    :return:
    """

    if not cauldron.project or not cauldron.project.internal_project:
        environ.output.fail().notify(
            kind='ERROR',
            code='NO_OPEN_PROJECT',
            message='No project is open. Step commands require an open project'
        ).console(
            whitespace=1
        )
        return

    if not action:
        actions.echo_steps()
        return

    if action[0] == 'list':
        actions.echo_steps()
        return

    if len(action) < 2:
        environ.output.fail().notify(
            kind='ABORTED',
            code='NO_STEP_NAME',
            message='A step name is required for this command'
        ).console(
            whitespace=1
        )
        return

    if action[0] == 'add':
        actions.create_step(
            action[1],
            position=position,
            title=title.strip('"') if title else title
        )
        return

    if action[0] == 'modify':
        actions.modify_step(
            name=action[1],
            new_name=new_name,
            title=title,
            position=position
        )

    if action[0] == 'remove':
        actions.remove_step(
            name=action[1],
            keep_file=keep
        )


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


