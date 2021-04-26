import functools
import pathlib
import random
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import cauldron
from cauldron import runner


def _mock_reload_module(history: dict, path: str, library_directory: str):
    """Mocked version of the runner.__init__._reload_module function."""
    output = {"path": path, "library_directory": library_directory}
    if path not in history and random.random() > 0.5:
        history[path] = output
        raise ValueError("Faking that this did not go well for the first time.")

    history[path] = output
    return output


@patch("cauldron.runner._reload_module")
def test_reload(reload_module: MagicMock):
    """Should reload as expected."""
    history = {}
    reload_module.side_effect = functools.partial(_mock_reload_module, history)
    library_directory = pathlib.Path(cauldron.__file__).resolve().parent
    output = runner.reload_libraries([None, str(library_directory)])

    me = pathlib.Path(__file__).resolve()
    root = pathlib.Path(cauldron.__file__).resolve()
    keys = list(history.keys())
    assert keys.index(str(me)) < keys.index(str(root)), """
        Expecting deeper hierarchy to be reloaded first.
        """

    assert output, "Expect a non-empty list returned."


@patch("cauldron.runner._reload_module")
def test_reload_failure(reload_module: MagicMock):
    """Should raise RuntimeError if imports fail after many retries."""
    reload_module.side_effect = ValueError("Nope")
    library_directory = pathlib.Path(cauldron.__file__).resolve().parent

    with pytest.raises(RuntimeError):
        runner.reload_libraries([None, str(library_directory)])
