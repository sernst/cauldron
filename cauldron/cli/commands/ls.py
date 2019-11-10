import os
import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.environ import Response
from cauldron.session.projects import specio

NAME = 'ls'
DESCRIPTION = (
    """
    Displays current directory information to help with navigation.
    """
)
SYNCHRONOUS = True


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """Populate the argument parser for the ls command invocation."""
    parser.add_argument('directory', default=None, nargs='?')


def _shorten_path(path: str) -> str:
    if len(path) > 40:
        return '{}...{}'.format(path[:12], path[-21:])
    return path


def _pretty_print(child: dict, is_file: bool = False) -> str:
    """Converts a child folder entry into a console display string."""
    if is_file:
        prefix = 4 * ' '
        icon = '~'
        name = child['name']
    else:
        prefix = 2 * ' '
        icon = '*' if child['spec'] else '-'
        name = child['folder']

    return '{}{} {}'.format(prefix, icon, name)


def execute(
        context: cli.CommandContext,
        directory: str = None
) -> Response:
    """Execute listing of current directory."""
    response = context.response

    current_directory = environ.paths.clean(directory or os.curdir)
    parent_directory = os.path.dirname(current_directory)

    try:
        items = os.listdir(current_directory)
    except PermissionError as error:
        return (
            response
            .fail(
                code='PERMISSION_DENIED',
                message='Access denied to "{}"'.format(current_directory),
                error=error
            )
            .console(whitespace=1)
            .response
        )

    children = [
        {'folder': item, 'parent': current_directory}
        for item in items
        if os.path.isdir(os.path.join(current_directory, item))
        and not item.startswith('.')
    ]

    for child in children:
        directory = os.path.join(child['parent'], child['folder'])
        path = os.path.join(directory, 'cauldron.json')
        child.update(
            directory=directory,
            short=_shorten_path(directory),
            spec=specio.get_project_info(path)
        )

    children = list(sorted(children, key=lambda c: c['folder'].lower()))

    files = [
        {'name': name, 'path': os.path.join(current_directory, name)}
        for name in os.listdir(current_directory)
        if os.path.isfile(os.path.join(current_directory, name))
        and not name.startswith('.')
    ]

    display = '\n'.join(
        [_pretty_print(c) for c in children]
        + [_pretty_print(f, True) for f in files]
    )

    standard_locations = [
        {'label': 'Parent Directory', 'directory': parent_directory},
        {'label': 'Home Directory', 'directory': '~'}
    ]

    rc = environ.remote_connection
    project = cauldron.project.get_internal_project(0.1)
    if project:
        standard_locations.append({
            'label': 'Project Directory',
            'directory': project.source_directory
        })
    elif rc.active and rc.local_project_directory:
        standard_locations.append({
            'label': 'Project Directory',
            'directory': rc.local_project_directory
        })

    if os.name == 'nt':
        standard_locations += [
            {
                'label': '{} Drive'.format(chr(x)),
                'directory': '{}:'.format(chr(x))
            }
            for x in range(65, 90)
            if os.path.exists('{}:'.format(chr(x)))
        ]

    return (
        response
        .update(
            standard_locations=standard_locations,
            # A None parent directory signifies that the current directory is
            # the root directory.
            parent_directory=(
                parent_directory
                if parent_directory != current_directory else
                None
            ),
            spec=specio.get_project_info(current_directory),
            current_directory=current_directory,
            shortened_directory=_shorten_path(current_directory),
            children=children,
            current_files=files,
        )
        .notify(
            kind='DIRECTORY',
            code='DIRECTORY_LISTING',
            message='\n{}\n\n{}'.format(current_directory, display)
        )
        .console(whitespace=1)
        .response
    )
