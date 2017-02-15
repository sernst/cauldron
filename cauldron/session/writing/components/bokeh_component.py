import os
import typing

from cauldron import cli
from cauldron import environ
from cauldron.session import projects
from cauldron.session.writing import file_io
from cauldron.session.writing.components import definitions
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE

BOKEH_WARNING = cli.reformat(
    """
    [WARNING]: Bokeh library is not installed. Unable to
        include library dependencies, which may result in
        HTML rendering errors. To resolve this make sure
        you have installed the Bokeh library.
    """
)


def create(project: 'projects.Project') -> COMPONENT:
    """
    :return:
    """

    try:
        from bokeh.resources import Resources as BokehResources
        bokeh_resources = BokehResources(mode='absolute')
    except Exception:
        bokeh_resources = None

    if bokeh_resources is None:
        environ.log(BOKEH_WARNING)
        return COMPONENT([], [])

    return definitions.merge_components(
        _assemble_component(
            project,
            'bokeh-css',
            ['bokeh', 'bokeh.css'],
            bokeh_resources.css_files
        ),
        _assemble_component(
            project,
            'bokeh-js',
            ['bokeh', 'bokeh.js'],
            bokeh_resources.js_files
        )
    )


def _assemble_component(
        project: 'projects.Project',
        name: str,
        slug: typing.List[str],
        source_paths: typing.List[str]
) -> COMPONENT:
    """

    :param project:
    :param name:
    :param slug:
    :param source_paths:
    :return:
    """

    return COMPONENT(
        includes=[WEB_INCLUDE(
            name=name,
            src='/{}'.format('/'.join(slug))
        )],
        files=[file_io.FILE_WRITE_ENTRY(
            path=os.path.join(project.output_directory, *slug),
            contents='\n'.join(map(_get_file_contents, source_paths))
        )]
    )


def _get_file_contents(source_path: str) -> str:
    """

    :param source_path:
    :return:
    """

    with open(source_path, 'r') as fp:
        return fp.read()
