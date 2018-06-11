import os

import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestSteps(scaffolds.ResultsTest):
    """Test suite for the steps module"""

    def test_steps_add(self):
        """Should add a step"""
        support.create_project(self, 'bob')
        project = cauldron.project.get_internal_project()

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(
            os.path.join(project.source_directory, 'S01-first.py')
        ))

    def test_steps_muting(self):
        """Should mute a step"""
        support.create_project(self, 'larry')

        support.run_command('steps add first.py')

        r = support.run_command('steps mute S01-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps unmute S01-first.py')
        self.assertFalse(r.failed, 'should nto have failed')

    def test_steps_modify(self):
        """Should modify a step"""
        response = support.create_project(self, 'lindsey')
        self.assertFalse(
            response.failed,
            Message(
                'should not have failed to create project',
                response=response
            )
        )

        project = cauldron.project.get_internal_project()
        directory = project.source_directory

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

    def test_steps_remove(self):
        """Should remove a step"""
        support.create_project(self, 'angelica')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S01-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S01-fake.py')
        self.assertTrue(r.failed, 'should have failed')

    def test_steps_remove_renaming(self):
        STEP_COUNT = 6

        support.create_project(self, 'bellatrix')
        results = [support.run_command('steps add') for i in range(STEP_COUNT)]

        has_failure = any([r.failed for r in results])
        self.assertFalse(has_failure, 'Failed to add step')

        r = support.run_command('steps remove S02.py')
        self.assertFalse(r.failed, 'Removal should have succeeded')

        project = cauldron.project.get_internal_project()
        step_names = [s.definition.name for s in project.steps]

        for i in range(STEP_COUNT - 1):
            self.assertEqual('S0{}.py'.format(i + 1), step_names[i])

    def test_steps_list(self):
        """Should list steps"""
        support.create_project(self, 'angelica')
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

    def test_autocomplete(self):
        """Should autocomplete steps command"""
        support.create_project(self, 'gina')
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

    def test_modify_move(self):
        """..."""
        support.create_project(self, 'harvey')
        support.add_step(self, contents='#S1')
        support.add_step(self, contents='#S2')

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

        with open(step['source_path'], 'r') as f:
            contents = f.read()

        self.assertEqual(contents.strip(), '#S2', Message(
            'Step 2 should now be Step 1',
            response=r
        ))

    def test_remote(self):
        """Should function remotely"""
        support.create_project(self, 'nails')
        project = cauldron.project.get_internal_project()

        support.run_remote_command('open "{}" --forget'.format(
            project.source_directory
        ))
        project = cauldron.project.get_internal_project()

        added_response = support.run_remote_command('steps add')
        self.assertTrue(added_response.success, Message(
            'Add Step Failed',
            response=added_response
        ))

        self.assertEqual(len(project.steps), 1)
