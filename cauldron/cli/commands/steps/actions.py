import os
import typing
import shutil

import cauldron
from cauldron import environ
from cauldron.session.projects import Project


def index_from_location(project: Project, location: str = None) -> int:
    """

    :param project:
    :param location:
    :return:
    """

    if location is None:
        return None

    if isinstance(location, (int, float)):
        return int(location)

    if isinstance(location, str):
        location = location.strip('"')

        try:
            location = int(location)
            return None if location < 0 else location
        except Exception:
            index = project.index_of_step(location)
            if index is not None:
                return index + 1
            else:
                return None

    return None


def echo_steps():
    """

    :return:
    """

    project = cauldron.project.internal_project

    if len(project.steps) < 1:
        environ.output.update(
            steps=[]
        ).notify(
            kind='SUCCESS',
            code='ECHO_STEPS',
            message='No steps in project'
        ).console(
            """
            [NONE]: This project does not have any steps yet. To add a new
                step use the command:

                steps add [YOUR_STEP_NAME]

                and a new step will be created in this project.
            """,
            whitespace=1
        )
        return

    environ.output.update(
        steps=[ps.kernel_serialize() for ps in project.steps]
    ).notify(
        kind='SUCCESS',
        code='ECHO_STEPS'
    ).console_header(
        'Project Steps',
        level=3
    ).console(
        '\n'.join(['* {}'.format(ps.definition.name) for ps in project.steps]),
        indent_by=2,
        whitespace_bottom=1
    )


def create_step(
        name: str,
        position: typing.Union[str, int],
        title: str = None
) -> str:
    """

    :param name:
    :param position:
    :param title:
    :return:
    """

    name = name.strip('"')
    title = title.strip('"') if title else title

    project = cauldron.project.internal_project
    position = index_from_location(project, position)

    step_data = {'name': name}
    if title:
        step_data['title'] = title

    result = project.add_step(step_data, index=position)

    if not os.path.exists(result.source_path):
        with open(result.source_path, 'w+') as f:
            f.write('')

    project.save()

    environ.output.update(
        project=project.kernel_serialize(),
        step_name=result.definition.name
    ).notify(
        kind='CREATED',
        code='STEP_CREATED',
        message='"{}" step has been created'.format(result.definition.name)
    ).console(
        whitespace=1
    )


def remove_step(name: str, keep_file: bool = False):
    """

    :param name:
    :param keep_file:
    :return:
    """

    project = cauldron.project.internal_project
    step = project.remove_step(name)
    if not step:
        environ.output.fail().notify(
            kind='ABORTED',
            code='NO_SUCH_STEP',
            message='Step "{}" not found. Unable to remove.'.format(name)
        ).kernel(
            name=name
        ).console(
            whitespace=1
        )
        return False

    project.save()

    if not keep_file:
        os.remove(step.source_path)

    environ.output.update(
        project=project.kernel_serialize()
    ).notify(
        kind='SUCCESS',
        code='STEP_REMOVED',
        message='Removed "{}" step from project'.format(name)
    ).console(
        whitespace=1
    )
    return True


def modify_step(
        name: str,
        new_name: str = None,
        title: str = None,
        position: typing.Union[str, int] = None
):
    """

    :param name:
    :param new_name:
    :param title:
    :param position:
    :return:
    """

    project = cauldron.project.internal_project

    name = name.strip('"')
    new_name = new_name.strip('"') if new_name else name
    step_data = {'name': new_name}

    title = title.strip('"') if title else None
    if title:
        step_data['title'] = title

    old_position = project.index_of_step(name)
    position = position.strip('"') if isinstance(position, str) else position
    if position is None:
        position = old_position

    old_step = project.remove_step(name)
    if not old_step:
        environ.output.fail().notify(
            kind='ABORTED',
            code='NO_SUCH_STEP',
            message='Unable to modify unknown step "{}"'.format(name)
        ).console(
            whitespace=1
        )
        return False

    index = index_from_location(project, position)

    new_step = project.add_step(step_data, index=index)

    if not os.path.exists(new_step.source_path):
        if os.path.exists(old_step.source_path):
            shutil.move(old_step.source_path, new_step.source_path)
        else:
            with open(new_step.source_path, 'w+') as f:
                f.write('')

    project.save()

    environ.output.update(
        project=project.kernel_serialize(),
        step_name=new_step.definition.name
    ).notify(
        kind='SUCCESS',
        code='STEP_MODIFIED',
        message='Step modifications complete'
    ).console(
        whitespace=1
    )

    return True


def toggle_muting(
        step_name: str,
        value: bool = None
):
    """

    :param step_name:
    :param value:
    :return:
    """

    project = cauldron.project.internal_project

    index = project.index_of_step(step_name)
    if index is None:
        return environ.output.fail().notify(
            kind='ERROR',
            code='NO_SUCH_STEP',
            message='No step found with name: "{}"'.format(step_name)
        ).kernel(
            name=step_name
        ).console()

    step = project.steps[index]
    if value is None:
        value = not bool(step.is_muted)

    step.is_muted = value

    return environ.output.notify(
        kind='SUCCESS',
        code='STEP_MUTE_ENABLED' if step.is_muted else 'STEP_MUTE_DISABLED',
        message='Muting has been {}'.format(
            'enabled' if step.is_muted else 'disabled'
        )
    ).kernel(
        project=project.kernel_serialize()
    ).console()
