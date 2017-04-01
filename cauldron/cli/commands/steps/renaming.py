import functools
import os
import tempfile
import typing
import zipfile
from collections import namedtuple

from cauldron.environ import Response
from cauldron.session import naming
from cauldron.session import projects
from cauldron.session.writing import file_io

STEP_RENAME = namedtuple('STEP_RENAME', [
    'id',
    'index',
    'old_name',
    'new_name',
    'old_path',
    'stash_path',
    'new_path'
])


def create_rename_entry(
        step: 'projects.ProjectStep',
        insertion_index: int = None,
        stash_path: str = None
) -> typing.Union[None, STEP_RENAME]:
    """
    Creates a STEP_RENAME for the given ProjectStep instance

    :param step:
        The ProjectStep instance for which the STEP_RENAME will be created
    :param insertion_index:
        An optional index where a step will be inserted as part of this
        renaming process. Allows files to be renamed prior to the insertion
        of the step to prevent conflicts.
    :param stash_path:
    :return:
    """

    project = step.project
    name = step.definition.name
    name_parts = naming.explode_filename(name, project.naming_scheme)
    index = project.index_of_step(name)
    name_index = index

    if insertion_index is not None and insertion_index <= index:
        # Adjusts indexing when renaming is for the purpose of
        # inserting a new step
        name_index += 1

    name_parts['index'] = name_index
    new_name = naming.assemble_filename(
        scheme=project.naming_scheme,
        **name_parts
    )

    if name == new_name:
        return None

    if not stash_path:
        fd, stash_path = tempfile.mkstemp(
            prefix='{}-{}--{}--'.format(step.reference_id, name, new_name)
        )
        os.close(fd)

    return STEP_RENAME(
        id=step.reference_id,
        index=index,
        old_name=name,
        new_name=new_name,
        old_path=step.source_path,
        stash_path=stash_path,
        new_path=os.path.join(step.project.source_directory, new_name)
    )


def create_backup(project: 'projects.Project') -> str:
    """

    :param project:
    :return:
    """

    backup_path = os.path.join(
        project.source_directory,
        'rename-backup.tmp.zip'
    )

    zf = zipfile.ZipFile(backup_path, mode='w')
    for s in project.steps:
        zf.write(filename=s.source_path, arcname=s.filename)

    zf.close()
    return backup_path


def stash_source(step_rename: STEP_RENAME) -> STEP_RENAME:
    """

    :param step_rename:
    :return:
    """

    file_io.copy(file_io.FILE_COPY_ENTRY(
        source=step_rename.old_path,
        destination=step_rename.stash_path
    ))

    if not os.path.exists(step_rename.stash_path):
        raise FileNotFoundError(
            'Unable to stash step file {}'.format(step_rename.old_name)
        )

    os.remove(step_rename.old_path)
    if os.path.exists(step_rename.old_path):
        raise FileExistsError(
            'Unable to remove existing step {}'.format(step_rename.old_name)
        )

    return step_rename


def unstash_source(step_rename: STEP_RENAME) -> STEP_RENAME:
    """

    :param step_rename:
    :return:
    """

    file_io.copy(file_io.FILE_COPY_ENTRY(
        source=step_rename.stash_path,
        destination=step_rename.new_path
    ))

    if not os.path.exists(step_rename.new_path):
        raise FileNotFoundError(
            'Failed to rename step file to {}'.format(step_rename.new_path)
        )

    try:
        os.remove(step_rename.stash_path)
    except PermissionError:
        pass

    return step_rename


def update_steps(
        project: 'projects.Project',
        step_renames: typing.List[STEP_RENAME]
) -> dict:
    """

    :param project:
    :param step_renames:
    :return:
    """

    result = dict()
    for step_rename in step_renames:
        step = project.get_step_by_reference_id(step_rename.id)
        step.definition.name = step_rename.new_name
        result[step_rename.old_name] = dict(
            name=step.definition.name,
            title=step.definition.title
        )

    return result


def synchronize_step_names(
        project: 'projects.Project',
        insert_index: int = None
) -> Response:
    """
    :param project:
    :param insert_index:
    """

    response = Response()
    response.returned = dict()

    if not project.naming_scheme:
        return response

    create_mapper_func = functools.partial(
        create_rename_entry,
        insertion_index=insert_index
    )

    step_renames = list([create_mapper_func(s) for s in project.steps])
    step_renames = list(filter(lambda sr: (sr is not None), step_renames))

    if not step_renames:
        return response

    try:
        backup_path = create_backup(project)
    except Exception as err:
        return response.fail(
            code='RENAME_BACKUP_ERROR',
            message='Unable to create backup name',
            error=err
        ).response

    try:
        step_renames = list([stash_source(sr) for sr in step_renames])
        step_renames = list([unstash_source(sr) for sr in step_renames])
    except Exception as err:
        return response.fail(
            code='RENAME_FILE_ERROR',
            message='Unable to rename files',
            error=err
        ).response

    response.returned = update_steps(project, step_renames)
    project.save()

    try:
        os.remove(backup_path)
    except PermissionError:
        pass

    return response
