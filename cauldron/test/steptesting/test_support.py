from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pytest import mark

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


MOCK_STEP_NAMES = [
    'S01-Foo.py',
    'S02-Bar.py',
    'S03-FooBar.py',
    'S04-Spam.py',
    'S05-Bar.py',
    'S06-Pam.py',
]

FIND_SCENARIOS = (
    ('S03-FooBar.py', MOCK_STEP_NAMES[2]),
    ('S04-Spam.py', MOCK_STEP_NAMES[3]),
    ('S04-Spam', MOCK_STEP_NAMES[3]),
    ('Spam', MOCK_STEP_NAMES[3]),
    ('Foo', MOCK_STEP_NAMES[0]),
    ('S99', None),
    ('Bar', MOCK_STEP_NAMES[1]),
    ('Pam', MOCK_STEP_NAMES[5]),
)


@mark.parametrize('lookup, expected', FIND_SCENARIOS)
def test_find_matching_step(lookup: str, expected: str):
    """Should find the expected matching step for the given scenario."""
    steps = []
    for name in MOCK_STEP_NAMES:
        step = MagicMock()
        step.name = name
        step.definition.name = name
        steps.append(step)

    project = MagicMock(steps=steps)

    observed = support.find_matching_step(project, lookup)
    if expected is None:
        assert observed is None, 'Expect no step match.'
    else:
        assert observed.definition.name == expected, """
            Expect the lookup "{lookup}" to match the step name "{expected}".
            """.format(lookup=lookup, expected=expected)
