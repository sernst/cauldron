from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock

from cauldron.session import projects


def test_no_project_defaults():
    """
    A ProjectStep without a Project reference should properly default
    its properties and values.
    """
    ps = projects.ProjectStep()
    assert -1 == ps.index
    assert [] == ps.web_includes
    assert ps.source_path is None


def test_is_dirty_branches():
    """
    ProjectStep should remain dirty until it has been properly
    initialized and run.
    """
    ps = projects.ProjectStep()
    assert ps.is_dirty(), 'Expected to always starts dirty'

    ps._is_dirty = False
    assert ps.is_dirty(), 'Expected dirty because not modified is None'

    ps.last_modified = 1
    assert not ps.is_dirty(), 'Expected not dirty without valid source path'


def test_elapsed_time():
    """Should return correct elapsed timestamp as a string."""
    dt = datetime.utcnow()
    ps = projects.ProjectStep()
    ps.start_time = dt
    ps.end_time = dt + timedelta(seconds=128.252525)
    result = ps.get_elapsed_timestamp()
    assert '02:08.25' == result


def test_clear_dom():
    """Should clear the dom for the step."""
    ps = projects.ProjectStep(project=MagicMock())
    ps.dumps = MagicMock()
    ps.mark_dirty(False, force=False)
    ps.report.body.append('FOO')

    ps.clear_dom()
    assert ps.is_dirty(), """
        Expect the step to be dirty when the dom is cleared.
        """
    assert [] == ps.report.body, """
        Expect the report body to emptied.
        """
