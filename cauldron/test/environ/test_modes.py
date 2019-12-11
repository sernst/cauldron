import itertools
import typing
from unittest.mock import patch

from cauldron.environ import modes
from pytest import mark

POSSIBILITIES = {
    'is_ui': modes.UI,
    'is_test': modes.TESTING,
    'is_interactive': modes.INTERACTIVE,
    'is_single_run': modes.SINGLE_RUN,
    'is_server': modes.SERVER,
}

SCENARIOS = [
    dict(combination)
    for combination
    in itertools.combinations_with_replacement(POSSIBILITIES.items(), 2)
]


@mark.parametrize('scenario', SCENARIOS)
def test_modes(scenario: typing.Dict[str, str]):
    """Should identify according to the expected results."""
    em = modes.ExposedModes
    patch_path = 'cauldron.environ.modes._current_modes'
    with patch(patch_path, new=[]):
        for m in scenario.values():
            modes.add(m)

        assert em.is_interactive() == ('is_interactive' in scenario)
        assert em.is_server() == ('is_server' in scenario)
        assert em.is_single_run() == ('is_single_run' in scenario)
        assert em.is_test() == ('is_test' in scenario)
        assert em.is_ui() == ('is_ui' in scenario)

        for m in scenario.values():
            modes.remove(m)
        assert not modes._current_modes
