from cauldron.test.support import mocking
import pytest


def test_patched_import():
    """Should successfully import the specified package."""
    with mocking.ImportPatcher() as mocked_importer:
        import sys
        assert hasattr(sys, 'path')


def test_patched_import_error():
    """Should raise import error."""

    with mocking.ImportPatcher() as mocked_importer:
        mocked_importer.error_on = ['sys']
        with pytest.raises(ImportError):
            import sys
