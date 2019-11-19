import time

from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui import statuses


@patch('cauldron.session.writing.step_writer.serialize')
@patch('cauldron.session.writing.save')
@patch('cauldron.project.get_internal_project')
def test_get_status(
        get_internal_project: MagicMock,
        writing_save: MagicMock,
        step_writer_serialize: MagicMock,
):
    """Should return dict-serialized status information."""
    step = MagicMock()
    step.last_modified = time.time() + 1000
    step.report.last_update_time = time.time() + 1000
    step.definition.name = 'bar'
    step.is_running = True

    step_data = MagicMock()
    step_data._asdict.return_value = {'name': 'bar'}
    step_writer_serialize.return_value = step_data

    project = MagicMock()
    project.steps = [step]
    project.kernel_serialize.return_value = {'name': 'foo'}

    get_internal_project.return_value = project

    response = statuses.get_status(0)

    assert response['success'], """
        Expect the status process to be successful.
        """
    assert {'name': 'foo'} == response['data']['project'], """
        Expect the kernel serialized project to be present.
        """
    assert 1 == writing_save.call_count, """
        Expect the single running step to be saved during
        serialization.
        """

    step_changes = response['data']['step_changes']
    expected = [{
        'name': 'bar',
        'action': 'updated',
        'step': {'name': 'bar'},
        'written': True
    }]
    assert expected == step_changes


@patch('cauldron.session.writing.step_writer.serialize')
@patch('cauldron.project.get_internal_project')
def test_get_status_no_project(
        get_internal_project: MagicMock,
        step_writer_serialize: MagicMock,
):
    """Should return status information with no project data."""
    get_internal_project.return_value = None

    response = statuses.get_status(0, force=True)

    assert response['success'], """
        Expect the status process to be successful.
        """
    assert response['data']['project'] is None, """
        Expect there to be no project data.
        """
    assert 0 == step_writer_serialize.call_count, """
        Expect no step serialization to be carried out.
        """
    assert [] == response['data']['step_changes'], """
        Expect no step changes to exist without project data.
        """
    assert response['hash'].startswith('forced-'), """
        Expect a forced call to have a forced hash.
        """
