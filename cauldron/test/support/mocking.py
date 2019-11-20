from unittest.mock import MagicMock


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
