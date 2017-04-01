import typing
import os

from cauldron import cli
from cauldron import environ
from cauldron.session import projects
from cauldron.session.writing import file_io
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE

PLOTLY_WARNING = cli.reformat(
    """
    [WARNING]: Plotly library is not installed. Unable to
        include library dependencies, which may result in
        HTML rendering errors. To resolve this make sure
        you have installed the Plotly library.
    """
)


def get_version_one_path() -> typing.Union[str, None]:
    try:
        from plotly.offline import offline as plotly_offline
    except Exception:
        return None

    return os.path.join(
        environ.paths.clean(os.path.dirname(plotly_offline.__file__)),
        'plotly.min.js'
    )


def get_version_two_path() -> typing.Union[str, None]:
    try:
        import plotly
    except Exception:
        return None

    return os.path.join(
        environ.paths.clean(os.path.dirname(plotly.__file__)),
        'package_data',
        'plotly.min.js'
    )


def get_source_path() -> typing.Union[str, None]:

    source_path = get_version_one_path()
    if source_path is None:
        environ.log(PLOTLY_WARNING)
        return None
    elif not os.path.exists(source_path):
        source_path = get_version_two_path()

    return source_path


def create(project: 'projects.Project') -> COMPONENT:
    """
    :param project:
    :return:
    """

    source_path = get_source_path()
    if not source_path:
        return COMPONENT([], [])

    output_slug = 'components/plotly/plotly.min.js'
    output_path = os.path.join(project.output_directory, output_slug)

    return COMPONENT(
        includes=[WEB_INCLUDE(
            name='plotly',
            src='/{}'.format(output_slug)
        )],
        files=[file_io.FILE_COPY_ENTRY(
            source=source_path,
            destination=output_path
        )]
    )
