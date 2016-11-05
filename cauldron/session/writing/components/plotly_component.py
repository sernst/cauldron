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


def create(project: 'projects.Project') -> COMPONENT:
    """
    :param project:
    :return:
    """

    try:
        from plotly.offline import offline as plotly_offline
    except Exception:
        plotly_offline = None

    if plotly_offline is None:
        environ.log(PLOTLY_WARNING)
        return COMPONENT([], [])

    source_path = os.path.join(
        environ.paths.clean(os.path.dirname(plotly_offline.__file__)),
        'plotly.min.js'
    )

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
