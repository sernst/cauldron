import json
import os
import typing

from cauldron import environ
from cauldron import templating
from cauldron.session import projects
from cauldron.session.writing import components
from cauldron.session.writing import file_io
from cauldron.session.writing import html
from cauldron.session.writing import step as step_writer


def save(
        project: 'projects.Project',
        write_list: typing.List[tuple] = None
) -> typing.List[tuple]:
    """
    Computes the file write list for the current state of the project if no
    write_list was specified in the arguments, and then writes each entry in
    that list to disk.

    :param project:
        The project to be saved
    :param write_list:
        The file writes list for the project if one already exists, or None
        if a new writes list should be computed
    :return:
        The file write list that was used to save the project to disk
    """

    try:
        writes = (
            to_write_list(project)
            if write_list is None
            else write_list.copy()
        )
    except Exception as err:
        raise

    environ.systems.remove(project.output_directory)
    os.makedirs(project.output_directory)

    file_io.deploy(writes)
    return writes


def to_write_list(project: 'projects.Project') -> typing.List[tuple]:
    """

    :param project:
    :return:
    """

    project_component = components.project_component.create_many(
        project,
        project.settings.fetch('web_includes', [])
    )

    steps_data = [step_writer.serialize(s) for s in project.steps]
    file_writes = [item for sd in steps_data for item in sd.file_writes]
    file_writes.extend(project_component.files)

    def to_step_dict(step: step_writer.STEP_DATA) -> dict:
        out = step._asdict()
        del out['file_writes']
        return out

    project_includes = [inc._asdict() for inc in project_component.includes]

    file_writes.append(file_io.FILE_WRITE_ENTRY(
        path=project.output_path,
        contents=templating.render_template(
            'report.js.template',
            DATA=json.dumps({
                'steps': [to_step_dict(sd) for sd in steps_data],
                'includes': project_includes,
                'settings': project.settings.fetch(None),
                'cauldron_version': list(environ.version_info)
            })
        )
    ))

    file_writes.extend(list_asset_writes(project))
    file_writes.append(html.create(
        project,
        project.results_path,
        'display.html'
    ))

    return file_writes


def list_asset_writes(
        project: 'projects.Project'
) -> typing.List[file_io.FILE_COPY_ENTRY]:
    """
    Returns a list containing the file/directory writes that should be executed
    to deploy the project assets to the results folder. If the project has no
    assets an empty list is returned.

    :param project:
        The project for which the assets should be copied
    :return:
        A list containing the file copy entries for deploying project assets
    """

    source_directory = os.path.join(project.source_directory, 'assets')
    if not os.path.exists(source_directory):
        return []

    output_directory = os.path.join(project.output_directory, 'assets')
    return [file_io.FILE_COPY_ENTRY(
        source=source_directory,
        destination=output_directory
    )]
