import hashlib
import json
import typing

import cauldron
from cauldron import environ
from cauldron.session import projects
from cauldron.render.encoding import ComplexJsonEncoder
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


def get_running_step_changes(write: bool = False) -> list:
    """..."""
    project = cauldron.project.get_internal_project()

    running_steps = list(filter(
        lambda step: step.is_running,
        project.steps
    ))

    def get_changes(step):
        step_data = writing.step_writer.serialize(step)

        if write:
            writing.save(project, step_data.file_writes)

        return dict(
            name=step.definition.name,
            action='updated',
            step=step_data._asdict(),
            written=write
        )

    return [get_changes(step) for step in running_steps]


def get_step_changes_after(
        project: 'projects.Project',
        timestamp: float,
        write_running: bool = False
) -> typing.List[dict]:
    """..."""
    modified_steps = list(filter(
        lambda step: step.report.last_update_time >= timestamp,
        project.steps
    ))

    def get_changes(step):
        step_data = writing.step_writer.serialize(step)
        write = write_running and step.is_running
        if write:
            writing.save(project, step_data.file_writes)

        return dict(
            name=step.definition.name,
            action='updated',
            step=step_data._asdict(),
            written=write
        )

    return [get_changes(step) for step in modified_steps]
