import os
import time
import json
import typing

import cauldron
from cauldron import environ


def echo_steps():
    """

    :return:
    """

    project = cauldron.project.internal_project

    if len(project.steps) < 1:
        environ.log(
            """
            [NONE]: This project does not have any steps yet. To add a new
                step use the command:

                steps add [YOUR_STEP_NAME]

                and a new step will be created in this project.
            """,
            whitespace=1
        )
        return

    environ.log_header('Project Steps', level=3)
    message = []
    for ps in project.steps:
        message.append('* {}'.format(ps.definition.name))
    environ.log('\n'.join(message), indent_by=2, whitespace_bottom=1)


def create_step(filename: str, position: typing.Union[str, int]) -> str:
    """

    :param filename:
    :param position:
    :return:
    """

    filename = filename.strip('"')

    project = cauldron.project.internal_project

    if position is not None:
        if isinstance(position, str):
            position = position.strip('"')
        try:
            position = int(position)
            if position < 0:
                position = None
        except Exception:
            for index, s in enumerate(project.steps):
                if s.definition.name == position:
                    position = index + 1
                    break
            if not isinstance(position, int):
                position = None

    result = project.add_step(filename, index=position)

    if not os.path.exists(result.source_path):
        with open(result.source_path, 'w+') as f:
            f.write('')

    with open(project.source_path, 'r+') as f:
        project_data = json.load(f)

    steps = [ps.definition.serialize() for ps in project.steps]
    project_data['steps'] = steps

    with open(project.source_path, 'w+') as f:
        json.dump(project_data, f, indent=2, sort_keys=True)

    project.last_modified = time.time()

    environ.output.update(
        project=project.kernel_serialize(),
        step_name=result.definition.name
    )

    return result.definition.name


def rename_step(old_filename: str, new_filename: str, new_title: str = None):
    """

    :param old_filename:
    :param new_filename:
    :param new_title:
    :return:
    """

    old_name = old_filename.strip('"')
    new_name = new_filename.strip('"')

    new_title = new_title.strip('"') if new_title is not None else None
    project = cauldron.project.internal_project

    for step in project.steps:
        if step.name == old_name:
            step.name = new_name
