from unittest import mock
from unittest.mock import patch

from cauldron.environ.response import Response
from cauldron.test.support import scaffolds


class TestResponse(scaffolds.ResultsTest):
    """ """

    def test_get_response(self):
        """ should get the response back from the response message """

        r = Response()
        self.assertEqual(r, r.fail().get_response())

    def test_warn(self):
        """ should notify if warned is called """

        r = Response()
        r.warn('FAKE_WARN', key='VALUE')

        self.assertEqual(len(r.warnings), 1)
        self.assertEqual(r.warnings[0].message, 'FAKE_WARN')
        self.assertEqual(r.warnings[0].data['key'], 'VALUE')

    def test_debug_echo(self):
        """ should echo debug information """

        r = Response()
        r.debug_echo()

    def test_echo(self):
        """ should echo information """

        r = Response()
        r.warn('WARNING', something=[1, 2, 3], value=False)
        r.fail('ERROR')
        result = r.echo()
        self.assertGreater(result.find('WARNING'), 0)
        self.assertGreater(result.find('ERROR'), 0)

    def test_echo_parented(self):
        """ should call parent echo """

        r = Response()
        parent = Response().consume(r)

        func = mock.MagicMock()
        with patch.object(parent, 'echo', func):
            r.echo()
            func.assert_any_call()

    def test_consume_nothing(self):
        """ should abort consuming if there is nothing to consume """

        r = Response()
        r.consume(None)

    def test_grandparent(self):
        """ should parent correctly if parented """

        child = Response()
        parent = Response()
        grandparent = Response()

        grandparent.consume(parent)
        parent.consume(child)

        self.assertEqual(child.parent, grandparent)

    def test_update_parented(self):
        """ should update through parent """

        child = Response()
        parent = Response()
        parent.consume(child)

        child.update(banana='orange')
        self.assertEqual(parent.data['banana'], 'orange')

    def test_notify_parented(self):
        """ should notify through parent """

        child = Response()
        parent = Response()
        parent.consume(child)

        child.notify('SUCCESS', 'Good Stuff', 'GO-CAULDRON')
        self.assertEqual(len(parent.messages), 1)

        m = parent.messages[0]
        self.assertEqual(m.code, 'GO-CAULDRON')
        self.assertEqual(m.kind, 'SUCCESS')
        self.assertEqual(m.message, 'Good Stuff')

    def test_end_parented(self):
        """ should end the parent """

        child = Response()
        parent = Response()
        parent.consume(child)

        child.end()
        self.assertTrue(parent.ended)

    def test_logging(self):
        """ should log messages to the log """

        r = Response()
        r.notify(
            kind='TEST',
            code='TEST_MESSAGE',
            message='This is a test',
        ).console_header(
            'Harold'
        ).console(
            'Holly'
        ).console_raw(
            'Handy'
        )

        out = r.get_notification_log()
        self.assertGreater(out.find('Harold'), -1)
        self.assertGreater(out.find('Holly'), -1)
        self.assertGreater(out.find('Handy'), -1)

        r = Response.deserialize(r.serialize())
        compare = r.get_notification_log()
        self.assertEqual(out, compare)

    def test_self_consumption(self):
        """ should not consume itself and cause regression error """

        r = Response()
        r.consume(r)
