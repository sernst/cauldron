import builtins
import typing
from unittest.mock import MagicMock
from unittest.mock import patch

_reserved_import = builtins.__import__


def populate_open_mock(mocked_open: MagicMock) -> MagicMock:
    """
    Populates the specified MagicMock configured for use in mocking an `open`
    object used as a ContextManager:

        with open('foo.file') as f:
            f.read()

    Such that it can be patched as:

        @patch('cauldron.path.to.file.open')
        def test_something(opener: MagickMock):
            populate_open_mock(opener)
            opener.mocked_file.read.return_value = 'foo'
    """
    file = MagicMock(name='mocked_open.mocked_file')

    context = MagicMock(name='mocked_open.mocked_context')
    context.__enter__.return_value = file

    mocked_open.mocked_file = file
    mocked_open.mocked_context = context
    mocked_open.return_value = context

    return mocked_open


class MockImporter:
    """Mocks the 'builtins.__import__ function."""

    def __init__(
            self,
            error_on: typing.List[str] = None,
            error_message: str = 'Mock Import Error'
    ):
        self.error_on = error_on or []
        self.error_message = error_message

    def __call__(self, *args, **kwargs):
        if args and args[0] in self.error_on:
            raise ImportError(self.error_message)
        return _reserved_import(*args, **kwargs)


class ImportPatcher:
    """Patches the 'builtins.__import__ function with a MockImporter."""

    def __init__(self):
        self.mock_importer = MockImporter([])
        self._patch = patch(
            'builtins.__import__',
            new=self.mock_importer
        )

    def __enter__(self):
        self._patch.__enter__()
        return self.mock_importer

    def __exit__(self, *args, **kwargs):
        return self._patch.__exit__(*args)
