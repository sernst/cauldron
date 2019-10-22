import flask

import cauldron
from cauldron.runner import redirection
from cauldron import environ
from cauldron.ui import configs as ui_configs
from cauldron.ui.routes.apis.executions import runner

blueprint = flask.Blueprint(
    name='executions',
    import_name=__name__,
    url_prefix='{}/api'.format(ui_configs.ROOT_PREFIX)
)


@blueprint.route('/command/sync', methods=['POST'])
def command_sync():
    """
    Returns the current status of the cauldron kernel application, which is
    used to keep the
    :return:
    """
    return runner.execute(False)


@blueprint.route('/command/async', methods=['POST'])
def command_async():
    """
    Returns the current status of the cauldron kernel application, which is
    used to keep the
    :return:
    """
    r = ui_configs.ACTIVE_EXECUTION_RESPONSE
    if r is not None and r.thread and r.thread.is_alive():
        return (
            environ.Response()
            .fail(
                code='ACTION_BLOCKED',
                message='Another command is currently executing.',
            )
            .response
            .flask_serialize()
        )

    return runner.execute(True)


@blueprint.route('/command/abort', methods=['POST'])
def abort():
    """..."""
    step_changes = []
    response = ui_configs.ACTIVE_EXECUTION_RESPONSE
    ui_configs.ACTIVE_EXECUTION_RESPONSE = None

    should_abort = (
        response is not None
        and response.thread
        and response.thread.is_alive()
    )

    if should_abort:
        # Try to stop the thread gracefully first.
        response.thread.abort = True
        response.thread.join(2)

        try:
            # Force stop the thread explicitly
            if response.thread.is_alive():
                response.thread.abort_running()
        except Exception:
            pass

    project = cauldron.project.internal_project

    if project and project.current_step:
        step = project.current_step
        if step.is_running:
            step.is_running = False
            step.progress = 0
            step.progress_message = None
            step_changes.append(step.dumps())

        # Make sure this is called prior to printing response information to
        # the console or that will come along for the ride
        redirection.disable(step)

    # Make sure no print redirection will survive the abort process regardless
    # of whether an active step was found or not (prevents race conditions)
    redirection.restore_default_configuration()

    project_data = project.kernel_serialize() if project else None

    return (
        environ.Response()
        .update(project=project_data, step_changes=step_changes)
        .flask_serialize()
    )
