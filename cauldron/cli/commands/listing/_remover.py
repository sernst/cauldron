import os
import textwrap
import typing

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.listing import _utils
from cauldron.session.projects import specio


def ask_identifier(projects: typing.List[dict]) -> typing.Optional[str]:
    print('\n\n{projects}\n\n{message}'.format(
        projects=specio.to_display_list(projects),
        message=(
            '   Enter the number for the project you wish to be removed\n'
            '   from the recent history list:'
        )
    ))
    return input('\nNumber to remove (empty to abort): ') or None


def is_identifier_match(identifier: str, project: dict) -> bool:
    """
    Determines whether or not the specified identifier matches
    any of the criteria of the given project context data values
    and returns the result as a boolean.
    """
    matches = (
        '{:.0f}'.format(project.get('index', -1) + 1),
        project.get('uid', ''),
        project.get('name', '')
    )
    return next(
        (True for m in matches if identifier == m),
        False
    )


def execute_removal(
        context: cli.CommandContext,
        command_args: dict
) -> environ.Response:
    projects = _utils.get_recent_projects().specs
    identifier = command_args.get('identifier') or ask_identifier(projects)

    if identifier is None:
        return (
            context.response
            .fail(
                kind='ABORTED',
                code='NO_IDENTIFIER_SET',
                message='No project identifier specified for removal.'
            )
            .response
        )

    match = next(
        (p for p in projects if is_identifier_match(identifier, p)),
        None
    )
    if not match:
        return (
            context.response
            .fail(
                kind='ABORTED',
                code='NO_MATCH_FOUND',
                message='No matching project found to remove.'
            )
            .console(whitespace=1)
            .response
        )

    confirmed = command_args.get('yes', False)
    if not confirmed:
        print('\n\nRemove the following entry from recent project history?\n')
        print(textwrap.indent(specio.to_display(match), '   '))
        response = input('\nRemove from recent history [y/N]? ')
        confirmed = response.lower().startswith('y')
    else:
        print('\n\nRemoving project entry:\n')
        print(textwrap.indent(specio.to_display(match), '   '))
    print('\n\n')

    if not confirmed:
        return (
            context.response
            .notify(
                kind='ABORTED',
                code='USER_ABORTED',
                message='Removal command aborted.'
            )
            .console(whitespace=1)
            .response
        )

    paths = [
        p
        for p in environ.configs.fetch('recent_paths', [])
        if os.path.exists(p)
    ]
    paths.remove(match['directory']['absolute'])
    environ.configs.put(recent_paths=paths, persists=True)
    environ.configs.save()

    return (
        context.response
        .update(projects=_utils.get_recent_projects().specs)
        .notify(
            kind='REMOVED',
            code='REMOVED',
            message='Entry has been removed from recent project history.'
        )
        .console(whitespace=1)
        .response
    )
