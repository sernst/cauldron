import os
import time
import json

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
        message.append('* {}'.format(ps.id))
    environ.log('\n'.join(message), indent_by=2, whitespace_bottom=1)


def create_step(filename: str) -> str:
    """

    :param filename:
    :return:
    """

    project = cauldron.project.internal_project

    result = project.add_step(filename)

    if not os.path.exists(result.source_path):
        with open(result.source_path, 'w+') as f:
            f.write('')

    with open(project.source_path, 'r+') as f:
        project_data = json.load(f)

    steps = []

    for ps in project.steps:
        d = ps.definition
        if not d.get('folder') and d.get('name') == d.get('file'):
            steps.append(d['name'])
        else:
            steps.append(ps.definition)

    project_data['steps'] = steps

    with open(project.source_path, 'w+') as f:
        json.dump(project_data, f, indent=2, sort_keys=True)

    project.last_modified = time.time()

    return result.id
