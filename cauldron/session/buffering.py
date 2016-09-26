import io
import sys

from cauldron.cli.threads import abort_thread


class RedirectBuffer(io.TextIOWrapper):

    def __init__(self):
        self._bytesBuffer = io.BytesIO()
        super(RedirectBuffer, self).__init__(
            buffer=self._bytesBuffer,
            encoding=sys.stdout.encoding,
            write_through=True
        )

    def read(self, n=None):
        abort_thread()
        return super(RedirectBuffer, self).read(n)

    def write(self, s):
        abort_thread()
        return super(RedirectBuffer, self).write(s)

    def close(self):
        abort_thread()
        return super(RedirectBuffer, self).close()

    def detach(self, *args, **kwargs):
        abort_thread()
        return super(RedirectBuffer, self).detach()

    def fileno(self, *args, **kwargs):
        abort_thread()
        return super(RedirectBuffer, self).fileno()

    def flush(self, *args, **kwargs):
        abort_thread()
        return super(RedirectBuffer, self).flush()

    def readline(self, limit=-1):
        abort_thread()
        return super(RedirectBuffer, self).readline(limit)

    def seek(self, *args, **kwargs):
        abort_thread()
        return super(RedirectBuffer, self).seek(*args, **kwargs)

    def seekable(self):
        abort_thread()
        return super(RedirectBuffer, self).seekable()

    def truncate(self, size=None):
        abort_thread()
        return super(RedirectBuffer, self).truncate(size)

    def read_all(self) -> str:
        """
        Reads the current state of the buffer and returns a string those
        contents

        :return:
            A string for the current state of the print buffer contents
        """

        try:
            buffered_bytes = self._bytesBuffer.getvalue()
            return buffered_bytes.decode(sys.stdout.encoding)
        except Exception as err:
            return 'Print Buffer Error: {}'.format(err)

    def flush_all(self):
        """

        :return:
        """

        self.seek(0)
        contents = self.read()
        self.truncate(0)
        self.seek(0)

        return contents
