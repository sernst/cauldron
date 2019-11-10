import cauldron
from cauldron import environ
from cauldron.ui.statuses import _utils
from cauldron.ui.statuses._reconciler import merge_local_state  # noqa


def get_status(last_timestamp: float, force: bool = False):
    project = cauldron.project.get_internal_project(timeout=0)

    if project:
        project_data = project.kernel_serialize()
        step_changes = _utils.get_step_changes_after(
            project=project,
            timestamp=last_timestamp - 0.2,
            write_running=True
        )
    else:
        project_data = None
        step_changes = []

    response = environ.Response().update(
        version=environ.version,
        remote=environ.remote_connection.serialize(),
        project=project_data,
        step_changes=step_changes,
        view=environ.view,
    )

    results = response.serialize()
    results['hash'] = _utils.get_digest_hash(results, force)
    return results
