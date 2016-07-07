import io

class FauxBufferIO(object):

    def __init__(self, owner: 'BufferedStringIO'):
        self._owner = owner

    def write(self, contents):

        self._owner.write(contents.decode('ascii', 'ignore'))

    def writelines(self, lines):
        for l in lines:
            self.write(l)


class BufferedStringIO(io.StringIO):

    def __init__(self, *args, **kwargs):
        super(BufferedStringIO, self).__init__(*args, **kwargs)
        self.buffer = FauxBufferIO(self)


