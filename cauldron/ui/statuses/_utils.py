import hashlib
import json
import time
import typing

from cauldron.render.encoding import ComplexJsonEncoder
from cauldron.session import projects
from cauldron.session import writing


def get_digest_hash(response_data: dict, force: bool = False) -> str:
    """
    Creates a digest hash of the specified response_data argument,
    which is used to track response changes.

    :param response_data:
        The source data to create a hash for. Timestamp data from
        is zero-ed out so that it doesn't change the hash every
        time just because execution time has changed. Only
        meaningful changes will alter the hash.
    :param force:
        If True, a time-dependent hash will be returned instead,
        which is useful when reconciling state by forcibly making
        the hash unique.
    """
    if force:
        return 'forced-{}'.format(time.time())

    r = response_data.copy()
    r['timestamp'] = None
    serialized = json.dumps(r, cls=ComplexJsonEncoder)
    return hashlib.blake2b(serialized.encode()).hexdigest()


def _get_step_changes(
        project: 'projects.Project',
        step: 'projects.ProjectStep',
        write_running: bool
) -> typing.Dict[str, typing.Any]:
    """
    Returns a dictionary containing the step changes for the given
    project and step. If the step is running and write_running is
    True then the step dom will be written to the results as well.

    :param project:
        Project in which the step will be serialized and potentially
        saved.
    :param step:
        Step to serialize.
    :param write_running:
        Whether or not to write running step changes to disk as part
        of the serialization process.
    :return:
        A dictionary containing the serialized step change.
    """
    step_data = writing.step_writer.serialize(step)

    if write_running and step.is_running:
        writing.save(project, step_data.file_writes)

    return dict(
        name=step.definition.name,
        action='updated',
        step=step_data._asdict(),
        written=write_running and step.is_running
    )


def get_step_changes_after(
        project: 'projects.Project',
        timestamp: float,
        write_running: bool = False
) -> typing.List[dict]:
    """
    Creates a list of step changes for each step in the project that has
    been updated more recently than the timestamp (seconds since epoch)
    specified in the arguments.

    :param project:
        Project in which to serialized step change data.
    :param timestamp:
        Any step that was modified more recently than this timestamp
        (seconds since epoch) will be included in the step changes.
        Older step changes will be ignored.
    :param write_running:
        Whether or not to write running step changes to disk as part
        of the serialization process.
    :return:
        A list of dictionaries containing the serialized step changes.
    """
    return [
        _get_step_changes(project, step, write_running)
        for step in project.steps
        if step.report.last_update_time >= timestamp
        or (step.last_modified or 0) >= timestamp
    ]
