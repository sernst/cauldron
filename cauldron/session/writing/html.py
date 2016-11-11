import os

from cauldron import environ
from cauldron import templating
from cauldron.session import projects
from cauldron.session.writing import file_io


def create(
        project: 'projects.Project',
        destination_directory,
        destination_filename: str = None
) -> file_io.FILE_WRITE_ENTRY:
    """
    Creates a FILE_WRITE_ENTRY for the rendered HTML file for the given
    project that will be saved in the destination directory with the given
    filename.

    :param project:
        The project for which the rendered HTML file will be created
    :param destination_directory:
        The absolute path to the folder where the HTML file will be saved
    :param destination_filename:
        The name of the HTML file to be written in the destination directory.
        Defaults to the project uuid.
    :return:
        A FILE_WRITE_ENTRY for the project's HTML file output
    """

    template_path = environ.paths.resources('web', 'project.html')
    with open(template_path, 'r+') as f:
        dom = f.read()

    dom = dom.replace(
        '<!-- CAULDRON:EXPORT -->',
        templating.render_template(
            'notebook-script-header.html',
            uuid=project.uuid,
            version=environ.version
        )
    )

    if not destination_filename:
        destination_filename = '{}.html'.format(project.uuid)

    html_out_path = os.path.join(
        destination_directory,
        destination_filename
    )

    return file_io.FILE_WRITE_ENTRY(
        path=html_out_path,
        contents=dom
    )
