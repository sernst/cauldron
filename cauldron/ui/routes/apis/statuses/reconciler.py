import os

from cauldron import environ


def _mark_dirty_after(step_data: dict, timestamp: float) -> dict:
    """
    Modifies the step_data to mark it dirty if the step data is for
    a remote project and the remote file (on the local system) has
    been modified more recently than it has been synchronized to the
    kernel system.
    """
    path = step_data.get('remote_source_path')
    status = step_data.get('status')
    if not path or not status:
        return step_data

    is_dirty = (
        status.get('dirty', False)
        or not os.path.exists(path)
        or timestamp < os.path.getmtime(path)
    )
    step_data['dirty'] = is_dirty
    status['dirty'] = is_dirty
    return step_data


def localize_dirty_steps(project_data: dict) -> dict:
    """..."""
    if not project_data:
        return project_data

    last_timestamp = environ.remote_connection.sync_timestamp
    project_data['steps'] = [
        _mark_dirty_after(s, last_timestamp)
        for s in project_data.get('steps') or []
    ]
    return project_data
