from unittest.mock import MagicMock

from cauldron.session.writing import components


def test_get_components_unknown():
    """Should return an empty component for unknown component name."""
    result = components._get_components('foo', MagicMock())
    assert not result.files
    assert not result.includes
