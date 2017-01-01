import io
import sys

from cauldron.cli.threads import abort_thread


class RedirectBuffer(io.TextIOWrapper):
    """
    A class for intercepting and independently storing buffer writes for use
    within Cauldron step display.
    """

    def __init__(self, redirection_source):
        self.bytes_buffer = io.BytesIO()
        self.redirection_source = redirection_source

        super(RedirectBuffer, self).__init__(
            buffer=self.bytes_buffer,
            encoding=redirection_source.encoding,
            write_through=True
        )

    @property
    def source_encoding(self):
        if self.redirection_source.encoding:
            return self.redirection_source.encoding
        return 'utf8'

    def read_all(self) -> str:
        """
        Reads the current state of the buffer and returns a string those
        contents

        :return:
            A string for the current state of the print buffer contents
        """

        try:
            buffered_bytes = self.bytes_buffer.getvalue()
            if buffered_bytes is None:
                return ''

            return buffered_bytes.decode(self.source_encoding)
        except Exception as err:
            return 'Redirect Buffer Error: {}'.format(err)

    def flush_all(self) -> str:
        """

        :return:
        """

        self.bytes_buffer.seek(0)
        contents = self.bytes_buffer.read()
        self.bytes_buffer.truncate(0)
        self.bytes_buffer.seek(0)

        if contents is None:
            return ''

        return contents.decode(self.source_encoding)

    def write_both(self, *args, **kwargs):
        abort_thread()
        super(RedirectBuffer, self).write(*args, **kwargs)
        return self.redirection_source.write(*args, **kwargs)

    def __getattribute__(self, item):
        """

        :param item:
        :return:
        """

        abort_thread()

        if item == 'write':
            # Writing should be done to both the source buffer and the redirect
            # buffer so that they have identical copies of the same information
            # for their separate uses
            return self.write_both
        elif item == 'close':
            # The source buffer should not be closed. The redirect buffer is
            # what should be closed by calls to instances of this class
            return super(RedirectBuffer, self).__getattribute__(item)

        # Access the source buffer using a super call to prevent recursion
        source = super(RedirectBuffer, self) \
            .__getattribute__('redirection_source')

        if hasattr(source, item):
            # Preference should be given to the source buffer for all other
            # operations given that this class is a wrapper around the source
            # buffer with the only added functionality being the intercepting
            # and duplication of write operations
            return getattr(source, item)

        # If the source buffer doesn't have a particular attribute it should
        # an attribute specific to this class
        return super(RedirectBuffer, self).__getattribute__(item)
