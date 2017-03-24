import os
from cauldron.test.support import scaffolds
from cauldron.cli import sync


class TestSyncIo(scaffolds.ResultsTest):
    """ Tests for the cauldron.cli.sync.sync_io module """

    def test_packing(self):
        """ should pack and then unpack a string successfully """

        source = b'abcdefg'
        packed = sync.io.pack_chunk(source)
        unpacked = sync.io.unpack_chunk(packed)
        self.assertEqual(source, unpacked)

    def test_reading_chunks(self):
        """ should read this file and write an identical file """

        path = os.path.realpath(__file__)
        out = self.get_temp_path('test_reading_chunks', 'test.py')
        for chunk in sync.io.read_file_chunks(path, 100):
            sync.io.write_file_chunk(out, chunk)

        with open(path) as f:
            me = f.read()
        with open(out) as f:
            compare = f.read()

        self.assertEqual(me, compare)

    def test_reading_no_such_file(self):
        """ should abort reading chunks if no such file exists """

        fake_path = '{}.fake-file'.format(__file__)
        chunks = [c for c in sync.io.read_file_chunks(fake_path)]
        self.assertEqual(0, len(chunks))
