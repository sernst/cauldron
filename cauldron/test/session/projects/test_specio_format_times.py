import time

from pytest import mark

from cauldron.session.projects import specio

SCENARIOS = [
    (20, 'just now'),
    (3 * 60, '3 minutes ago'),
    (3 * 3600, '3 hours ago'),
    (4 * 86400, '4 days ago'),
    (6 * 7 * 86400, '6 weeks ago'),
    (367 * 86400, '1 year ago'),
    (3 * 365 * 86400, '3 years ago'),
]


@mark.parametrize('offset, expected', SCENARIOS)
def test_format_times(offset: float, expected: str):
    """Should return formatted time according to scenario expectation."""
    timestamp = time.time() - offset
    assert expected == specio.format_times(timestamp)['elapsed']
