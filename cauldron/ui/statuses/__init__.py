import cauldron
from cauldron import environ
from cauldron.ui.statuses import _utils
from cauldron.ui.statuses._reconciler import merge_local_state  # noqa


def get_status(last_timestamp: float, force: bool = False) -> dict:
    """
    Returns the current status of the cauldron process for updated
    display in the UI. This contains project information along with
    step changes and environmental configuration. The entire payload
    is hashed and that hash is included in the returned dictionary
    so that the UI only returns information when the hash has changed.

    :param last_timestamp:
        Epoch time in seconds since the last status update. This
        status update will include all changes made since that
        time.
    :param force:
        If forced, the hash will be certain to be different than
        the previous one, which is useful when trying to reconcile
        settings changes.
    :return:
        A dictionary containing the serialized request for the
        given status request.
    """
    project = cauldron.project.get_internal_project(timeout=0)

    if project:
        project_data = project.kernel_serialize()
        step_changes = _utils.get_step_changes_after(
            project=project,
            timestamp=last_timestamp - 1,
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
