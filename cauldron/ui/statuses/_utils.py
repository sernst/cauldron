import hashlib
import json
import time
import typing

from cauldron.render.encoding import ComplexJsonEncoder
from cauldron.session import projects
from cauldron.session import writing


def get_digest_hash(response_data: dict, force: bool = False) -> str:
    # We zero out the timestamp here so that it doesn't change the
    # hash every time just because execution time has changed.
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
    """..."""
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
    """..."""
    return [
        _get_step_changes(project, step, write_running)
        for step in project.steps
        if step.report.last_update_time >= timestamp
        or (step.last_modified or 0) >= timestamp
    ]
