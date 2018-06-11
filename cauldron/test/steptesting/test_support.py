from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import cauldron
from cauldron.steptest import support


@patch('time.sleep')
@patch('cauldron.cli.commander.execute')
def test_open_project(
        execute: MagicMock,
        sleep: MagicMock
):
    """Should fail to open project and eventually give up"""
    cauldron.project.unload()
    execute.return_value = MagicMock()

    with pytest.raises(RuntimeError):
        support.open_project('FAKE')

    assert 1 == execute.call_count, """
        Expected a single execute call to open the project.
        """
    assert 10 == sleep.call_count, """
        Expected sleep to be called repeatedly until the wait period
        for opening the project times out.
        """
