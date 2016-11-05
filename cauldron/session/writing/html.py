import os

from cauldron import environ
from cauldron import templating
from cauldron.session import projects
from cauldron.session.writing import file_io


def create(
        project: 'projects.Project',
        destination_directory: str = None,
        destination_filename: str = 'display.html'
) -> file_io.FILE_WRITE_ENTRY:
    """

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

    if not destination_directory:
        destination_directory = os.path.dirname(template_path)

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
