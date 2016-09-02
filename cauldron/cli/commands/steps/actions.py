import os
import shutil
import typing

import cauldron
from cauldron import environ
from cauldron.session import naming
from cauldron.session import writing
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
    index = index_from_location(project, position)
    if index is None:
        index = len(project.steps)

    name_parts = naming.explode_filename(name, project.naming_scheme)

    if not project.naming_scheme and not name_parts['name']:
        name_parts['name'] = naming.find_default_filename(
            [s.definition.name for s in project.steps]
        )

    name_parts['index'] = index
    name = naming.assemble_filename(
        scheme=project.naming_scheme,
        **name_parts
    )

    step_data = {'name': name}

    if title:
        step_data['title'] = title

    result = project.add_step(step_data, index=index)

    if not os.path.exists(result.source_path):
        with open(result.source_path, 'w+') as f:
            f.write('')

    project.save()

    index = project.steps.index(result)

    step_renames = synchronize_step_names()

    step_changes = [dict(
        name=result.definition.name,
        action='added',
        step=writing.write_step(result),
        after=None if index < 1 else project.steps[index - 1].definition.name
    )]

    environ.output.update(
        project=project.kernel_serialize(),
        step_name=result.definition.name,
        step_path=result.source_path,
        step_changes=step_changes,
        step_renames=step_renames
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

    step_renames = synchronize_step_names()

    step_changes = [dict(
        name=name,
        action='removed'
    )]

    environ.output.update(
        project=project.kernel_serialize(),
        step_changes=step_changes,
        step_renames=step_renames
    ).notify(
        kind='SUCCESS',
        code='STEP_REMOVED',
        message='Removed "{}" step from project'.format(name)
    ).console(
        whitespace=1
    )
    return True


def synchronize_step_names():
    """

    :return:
    """
    project = cauldron.project.internal_project
    results = dict()

    if not project.naming_scheme:
        return results

    for s in reversed(project.steps):
        name = s.definition.name
        name_parts = naming.explode_filename(name, project.naming_scheme)
        index = project.index_of_step(name)
        name_parts['index'] = index
        new_name = naming.assemble_filename(
            scheme=project.naming_scheme,
            **name_parts
        )

        if name == new_name:
            continue

        old_source_path = s.source_path
        s.definition.name = new_name

        if not os.path.exists(s.source_path):
            if os.path.exists(old_source_path):
                shutil.move(old_source_path, s.source_path)
            else:
                with open(s.source_path, 'w+') as f:
                    f.write('')

        results[name] = {
            'name': new_name,
            'title': s.definition.title
        }

    project.save()
    return results


def modify_step(
        name: str,
        new_name: str = None,
        position: typing.Union[str, int] = None,
        title: str = None
):
    """

    :param name:
    :param new_name:
    :param position:
    :param title:
    :return:
    """

    name = name.strip('"')
    new_name = new_name.strip('"') if new_name else name

    project = cauldron.project.internal_project
    old_index = project.index_of_step(name)

    if isinstance(position, str):
        new_index = index_from_location(project, position.strip('"'))
    elif position is not None:
        new_index = int(position)
    else:
        new_index = old_index

    if new_index > old_index:
        # If the current position of the step occurs before the new position
        # of the step, the new index has to be shifted by one to account for
        # the fact that this step will no longer be in this position when it
        # get placed in the position within the project
        new_index -= 1

    new_name_parts = naming.explode_filename(new_name, project.naming_scheme)
    new_name_parts['index'] = new_index

    if not project.naming_scheme and not new_name_parts['name']:
        new_name_parts['name'] = naming.find_default_filename(
            [s.definition.name for s in project.steps]
        )

    new_name = naming.assemble_filename(
        scheme=project.naming_scheme,
        **new_name_parts
    )

    if new_name == name and new_index == old_index:
        # Do not carry out any modifications if nothing was actually changed
        return

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

    step_data = {'name': new_name}
    if title is None:
        if old_step.definition.get('title'):
            step_data['title'] = old_step.definition['title']
    else:
        step_data['title'] = title.strip('"')

    new_step = project.add_step(step_data, new_index)

    project.save()

    if not os.path.exists(new_step.source_path):
        if os.path.exists(old_step.source_path):
            shutil.move(old_step.source_path, new_step.source_path)
        else:
            with open(new_step.source_path, 'w+') as f:
                f.write('')

    if new_index > 0:
        before_step = project.steps[new_index - 1].definition.name
    else:
        before_step = None

    step_renames = synchronize_step_names()
    step_renames[old_step.definition.name] = {
        'name': new_step.definition.name,
        'title': new_step.definition.title
    }

    step_changes = [dict(
        name=new_step.definition.name,
        action='modified',
        after=before_step
    )]

    environ.output.update(
        project=project.kernel_serialize(),
        step_name=new_step.definition.name,
        step_changes=step_changes,
        step_renames=step_renames
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
