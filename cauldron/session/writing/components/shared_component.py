import glob
import functools
import os

from cauldron import environ
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE


def create(name: str) -> COMPONENT:
    """

    :param name:
    :return:
    """

    component_directory = get_component_directory(name)
    if not os.path.exists(component_directory):
        return COMPONENT([], [])

    glob_path = os.path.join(component_directory, '**', '*')

    web_includes = []
    for file_path in glob.iglob(glob_path, recursive=True):
        web_includes.append(to_web_include(name, file_path))

    return COMPONENT(
        files=[],
        includes=list(filter(lambda w: w is not None, web_includes))
    )


def get_component_directory(component_name: str) -> str:
    """

    :param component_name:
    :return:
    """

    return environ.paths.resources('web', 'components', component_name)


def to_web_include(component_name: str, file_path: str) -> WEB_INCLUDE:
    """

    :param component_name:
    :param file_path:
    :return:
    """

    if not os.path.isfile(file_path):
        return None

    if not file_path.endswith('.css') and not file_path.endswith('.js'):
        return None

    component_directory = get_component_directory(component_name)
    slug = (
        file_path[len(component_directory):]
        .replace('\\', '/')
        .strip('/')
    )

    # web includes that start with a : are relative to the root
    # results folder, not the project itself. They are for shared
    # resource files
    return WEB_INCLUDE(
        name='components-{}-{}'.format(
            component_name,
            slug.replace('/', '_').replace('.', '_')
        ),
        src=':components/{}/{}'.format(component_name, slug)
    )
