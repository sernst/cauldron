import typing
import os
from os.path import realpath
from pytest import mark

from cauldron.environ import paths
from cauldron.test import support
from cauldron.test.support import scaffolds

PATH_SCENARIOS = [
    (None, lambda: realpath(os.curdir)),
    ('.', lambda: realpath(os.curdir)),
    (__file__, realpath(__file__)),
    ('~/bob', realpath(os.path.expanduser('~/bob'))),
    ('"~/bob"', realpath(os.path.expanduser('~/bob'))),
]


@mark.parametrize('value, expected', PATH_SCENARIOS)
def test_clean_path(
        value: str,
        expected: typing.Union[str, typing.Callable[[], str]]
):
    """Should clean path to be current directory."""
    observed = paths.clean(value)
    expected = expected if isinstance(expected, str) else expected()
    assert expected == observed
