from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui.routes.apis.executions import runner


@patch('cauldron.ui.routes.apis.executions.runner.ui_configs')
@patch('cauldron.ui.routes.apis.executions.runner.redirection')
@patch('cauldron.project.get_internal_project')
def test_abort(
    get_internal_project: MagicMock,
    redirection: MagicMock,
    ui_configs: MagicMock,
):
    """Should carry out an abort process on the active response thread."""
    active_response = MagicMock()
    active_response.thread.abort_running.side_effect = ValueError
    ui_configs.ACTIVE_EXECUTION_RESPONSE = active_response

    step = MagicMock()
    step.is_running = True
    project = MagicMock()
    project.current_step = step
    get_internal_project.return_value = project

    response = runner.abort()

    assert response.success
    assert redirection.disable.called
    assert redirection.restore_default_configuration.called
    assert not step.is_running, """
        Expect the current step to be stopped given that
        it was running.
        """
