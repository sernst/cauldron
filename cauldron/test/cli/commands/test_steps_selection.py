from unittest.mock import MagicMock

from cauldron import environ
from cauldron.cli.commands.steps import selection
from cauldron.test import support


def test_select_step():
    """Should select the specified step."""
    project = MagicMock()
    response = selection.select_step(environ.Response(), project, 'foo.py')
    assert support.has_success_code(response, 'SELECTED')


def test_select_step_failed():
    """Should fail to select the specified step if it does not exist."""
    project = MagicMock()
    project.select_step.return_value = None
    response = selection.select_step(environ.Response(), project, 'foo.py')
    assert support.has_error_code(response, 'NO_SUCH_STEP')
