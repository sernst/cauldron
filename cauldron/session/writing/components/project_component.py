import glob
import os
import typing
import functools

from cauldron import environ
from cauldron.session import projects
from cauldron.session.writing import file_io
from cauldron.session.writing.components import definitions
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE


def create(
        project: 'projects.Project',
        include_path: str
) -> COMPONENT:
    """
    Creates a COMPONENT instance for the project component specified by the
    include path

    :param project:
        The project in which the component resides
    :param include_path:
        The relative path within the project where the component resides
    :return:
        The created COMPONENT instance
    """

    source_path = environ.paths.clean(
        os.path.join(project.source_directory, include_path)
    )
    if not os.path.exists(source_path):
        return COMPONENT([], [])

    if os.path.isdir(source_path):
        glob_path = os.path.join(source_path, '**', '*')
        include_paths = glob.iglob(glob_path, recursive=True)
    else:
        include_paths = [source_path]

    destination_path = os.path.join(project.output_directory, include_path)

    return COMPONENT(
        includes=filter(
            lambda web_include: web_include is not None,
            map(functools.partial(to_web_include, project), include_paths)
        ),
        files=[file_io.FILE_COPY_ENTRY(
            source=source_path,
            destination=destination_path
        )]
    )


def create_many(
        project: 'projects.Project',
        include_paths: typing.List[str]
) -> COMPONENT:
    """
    Creates a single COMPONENT instance for all of the specified project
    include paths

    :param project:
        Project where the components reside
    :param include_paths:
        A list of relative paths within the project directory to files or
        directories that should be included in the project
    :return:
        The combined COMPONENT instance for all of the included paths
    """

    return definitions.merge_components(*map(
        functools.partial(create, project),
        include_paths
    ))


def to_web_include(
        project: 'projects.Project',
        file_path: str
) -> WEB_INCLUDE:
    """
    Converts the given file_path into a WEB_INCLUDE instance that represents
    the deployed version of this file to be loaded into the results project
    page

    :param project:
        Project in which the file_path resides
    :param file_path:
        Absolute path to the source file for which the WEB_INCLUDE instance
        will be created
    :return:
        The WEB_INCLUDE instance that represents the given source file
    """

    if not file_path.endswith('.css') and not file_path.endswith('.js'):
        return None

    slug = file_path[len(project.source_directory):]
    url = '/{}' \
        .format(slug) \
        .replace('\\', '/') \
        .replace('//', '/')

    return WEB_INCLUDE(name=':project:{}'.format(url), src=url)
