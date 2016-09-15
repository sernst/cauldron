import os
import sys

from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestSteps(scaffolds.ResultsTest):
    """

    """

    def test_steps_add(self):
        """
        """

        directory = support.initialize_project(self, 'bob')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(os.path.join(directory, 'S01-first.py')))

        support.run_command('close')

    def test_steps_muting(self):
        """
        """

        support.initialize_project(self, 'larry')

        support.run_command('steps add first.py')

        r = support.run_command('steps mute S01-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps unmute S01-first.py')
        self.assertFalse(r.failed, 'should nto have failed')

        support.run_command('close')

    def test_steps_modify(self):
        """
        """

        directory = support.initialize_project(self, 'lindsey')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(os.path.join(directory, 'S01-first.py')))

        r = support.run_command('steps modify S01-first.py --name="second.py"')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertFalse(
            os.path.exists(os.path.join(directory, 'S01-first.py'))
        )
        self.assertTrue(
            os.path.exists(os.path.join(directory, 'S01-second.py'))
        )

        support.run_command('close')

    def test_steps_remove(self):
        """
        """

        support.initialize_project(self, 'angelica')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S01-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S01-fake.py')
        self.assertTrue(r.failed, 'should have failed')

        support.run_command('close')

    def test_steps_list(self):
        """
        """

        support.initialize_project(self, 'angelica')
        r = support.run_command('steps list')
        self.assertEqual(len(r.data['steps']), 0, Message(
            'New project should have no steps to list',
            response=r
        ))

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

        if sys.platform == 'win32':
            # Autocomplete is not available on  windows
            return

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

    def test_modify_move(self):
        """

        :return:
        """

        support.initialize_project(self, 'harvey')
        support.add_step(self, '', '#S1')
        support.add_step(self, '', '#S2')

        r = support.run_command('steps list')
        step = r.data['steps'][-1]

        r = support.run_command(
            'steps modify {} --position=0'.format(step['name'])
        )
        self.assertFalse(r.failed, Message(
            'Failed to move step 2 to the beginning',
            response=r
        ))

        r = support.run_command('steps list')
        step = r.data['steps'][0]

        with open(step['source_path'], 'r+') as f:
            contents = f.read()

        self.assertEqual(contents.strip(), '#S2', Message(
            'Step 2 should now be Step 1',
            response=r
        ))

        support.run_command('close')
