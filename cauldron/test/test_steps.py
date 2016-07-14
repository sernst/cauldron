import os

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSteps(scaffolds.ResultsTest):
    """

    """

    def test_steps_add(self):
        """
        """

        directory = support.initialize_project(self, 'bob')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(os.path.join(directory, 'first.py')))

        support.run_command('close')

    def test_steps_muting(self):
        """
        """

        support.initialize_project(self, 'larry')

        support.run_command('steps add first.py')

        r = support.run_command('steps mute first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps unmute first.py')
        self.assertFalse(r.failed, 'should nto have failed')

        support.run_command('close')

    def test_steps_modify(self):
        """
        """

        directory = support.initialize_project(self, 'lindsey')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(os.path.join(directory, 'first.py')))

        r = support.run_command('steps modify first.py --name="second.py"')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertFalse(os.path.exists(os.path.join(directory, 'first.py')))
        self.assertTrue(os.path.exists(os.path.join(directory, 'second.py')))

        support.run_command('close')

    def test_steps_remove(self):
        """
        """

        support.initialize_project(self, 'angelica')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove fake.py')
        self.assertTrue(r.failed, 'should have failed')

        support.run_command('close')

    def test_steps_list(self):
        """
        """

        support.initialize_project(self, 'angelica')

        for v in ['a.py', 'b.md', 'c.html', 'd.rst']:
            r = support.run_command('steps add "{}"'.format(v))
            self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps list')
        self.assertFalse(r.failed, 'should not have failed')

        support.run_command('close')

    def test_autocomplete(self):
        """

        :return:
        """

        support.initialize_project(self, 'gina')
        support.add_step(self, 'a.py')
        support.add_step(self, 'b.py')

        result = support.autocomplete('steps a')
        self.assertIn('add', result)

        result = support.autocomplete('steps modify ')
        self.assertEqual(
            len(result), 2,
            'there are two steps in {}'.format(result)
        )

        result = support.autocomplete('steps modify a.py --')
        self.assertIn('name=', result)

        result = support.autocomplete('steps modify fake.py --position=')
        self.assertEqual(
            len(result), 2,
            'there are two steps in {}'.format(result)
        )

        support.run_command('close')
