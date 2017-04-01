import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron.cli.commands.steps import actions
from cauldron.cli.commands.steps import removal
from cauldron.cli.interaction import autocompletion
from cauldron.environ import Response
from cauldron.session import projects
from cauldron.cli import sync
from cauldron.cli.commands.open import opener as project_opener
from cauldron.cli.commands import sync as sync_command


NAME = 'steps'
DESCRIPTION = """
    Carry out an action on one or more steps within the currently opened
    project. The available actions are:
        * [add]: Creates a new step
        * [list]: Lists the steps within the currently opened project
        * [modify]: Modifies an existing step
        * [remove]: Removes an existing step from the project
        * [unmute]: Enables a step within the active project
        * [mute]: Disables a step within the active project
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

    if len(raw_args) < 1:
        assigned_args['action'] = 'list'
        return

    action = raw_args.pop(0).lower()
    assigned_args['action'] = action

    if action == 'add':
        parser.add_argument(
            'step_name',
            type=str,
            nargs='?',
            help=cli.reformat(
                """
                The name of the step you want to create
                """
            )
        )
    elif action != 'list':
        parser.add_argument(
            'step_name',
            type=str,
            help=cli.reformat(
                """
                The name of the step on which to carry out the steps action
                """
            )
        )

    if action in ['mute', 'unmute']:
        return

    if action in ['add', 'modify']:
        parser.add_argument(
            '-p', '--position',
            dest='position',
            type=str,
            default=None,
            help=cli.reformat(
                """
                Specifies the index where the step will be inserted, or the
                name of the step after which this new step will be inserted.
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

    if action == 'modify':
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

    if action == 'remove':
        parser.add_argument(
            '-k', '--keep',
            dest='keep',
            default=False,
            action='store_true',
            help=cli.reformat(
                """
                Whether or not to keep the source file when removing a step
                from a project
                """
            )
        )


def execute_remote(
        context: cli.CommandContext,
        action: str = None,
        step_name: str = None,
        position: str = None,
        title: str = None,
        new_name: str = None,
        keep: bool = False,
) -> Response:

    status_response = sync.comm.send_request(
        endpoint='/sync-status',
        remote_connection=context.remote_connection
    )
    if status_response.failed:
        return context.response.consume(status_response)

    source_directory = status_response.data['remote_source_directory']
    if not project_opener.project_exists(context.response, source_directory):
        return context.response

    context.response.consume(execute(
        context=context,
        action=action,
        step_name=step_name,
        position=position,
        title=title,
        new_name=new_name,
        keep=keep,
        project=projects.Project(source_directory)
    ))
    if context.response.failed:
        return context.response

    sync_response = sync_command.do_synchronize(
        context=cli.make_command_context(
            name='sync',
            response=context.response,
            remote_connection=context.remote_connection
        ),
        source_directory=source_directory,
        newer_than=status_response.data.get('sync_time', 0)
    )

    return context.response.consume(sync_response)


def execute(
        context: cli.CommandContext,
        action: str = None,
        step_name: str = None,
        position: str = None,
        title: str = None,
        new_name: str = None,
        keep: bool = False,
        project: 'projects.Project' = None
) -> Response:
    """

    :return:
    """

    response = context.response

    project = (
        project
        if project else
        cauldron.project.internal_project
    )

    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is open. Step commands require an open project'
        ).console(
            whitespace=1
        ).response

    if not action or action == 'list':
        actions.echo_steps(response, project)
        return response

    if action == 'add' and not step_name:
            step_name = ''
    elif not step_name:
        return response.fail(
            code='NO_STEP_NAME',
            message='A step name is required for this command'
        ).console(
            whitespace=1
        ).response

    step_name = step_name.strip('"')

    if action == 'add':
        return actions.create_step(
            response=response,
            project=project,
            name=step_name,
            position=position,
            title=title.strip('"') if title else title
        )

    if action == 'modify':
        actions.modify_step(
            response=response,
            project=project,
            name=step_name,
            new_name=new_name,
            title=title,
            position=position
        )
        return response

    if action == 'remove':
        return removal.remove_step(
            response=response,
            project=project,
            name=step_name,
            keep_file=keep
        )

    if action == 'unmute':
        actions.toggle_muting(
            response=response,
            project=project,
            step_name=step_name,
            value=False
        )
        return response

    if action == 'mute':
        actions.toggle_muting(
            response=response,
            project=project,
            step_name=step_name,
            value=True
        )
        return response


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
            ['add', 'list', 'remove', 'modify', 'unmute', 'mute']
        )

    action = parts[0]
    if action == 'list':
        return []

    project = cauldron.project.internal_project

    if len(parts) < 3 or parts[-1].startswith(('--position=', '-p ')):
        prefix = parts[-1]
        for remove in ['--position=', '-p ']:
            if prefix.startswith(remove):
                prefix = prefix[len(remove):]
                break
        prefix = prefix.strip().strip('"')

        step_names = [x.definition.name for x in project.steps]
        return autocompletion.match_in_path_list(
            segment,
            prefix,
            step_names
        )

    if parts[-1].startswith('-'):
        if action == 'list':
            return []

        shorts = []
        longs = []

        if action == 'remove':
            shorts.append('k')
            longs.append('keep')
        else:
            shorts += ['p', 't']
            longs += ['position=', 'title=']

        if action == 'modify':
            shorts.append('n')
            longs.append('name=')

        return autocompletion.match_flags(
            segment=segment,
            value=parts[-1],
            shorts=shorts,
            longs=longs
        )

    return []


