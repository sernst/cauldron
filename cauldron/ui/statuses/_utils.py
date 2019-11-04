import hashlib
import json
import typing

from cauldron import environ
from cauldron.render.encoding import ComplexJsonEncoder
from cauldron.session import projects
from cauldron.session import writing


def get_digest_hash(response: environ.Response) -> str:
    # We zero out the timestamp here so that it doesn't change the
    # hash every time just because execution time has changed.
    r = response.serialize()
    r['timestamp'] = None

    data = r['data']
    if data.get('project') and 'serial_time' in data['project']:
        data['project']['serial_time'] = None

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
