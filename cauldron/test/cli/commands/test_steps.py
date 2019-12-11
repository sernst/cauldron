import os
from unittest.mock import MagicMock
from unittest.mock import patch

import cauldron
from cauldron import environ
from cauldron.cli.commands import steps as steps_command
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message
from cauldron.test.support import server


class TestSteps(scaffolds.ResultsTest):
    """Test suite for the steps module"""

    def test_steps_add(self):
        """Should add a step"""
        support.create_project(self, 'bob')
        project = cauldron.project.get_internal_project()

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(
            os.path.join(project.source_directory, 'S02-first.py')
        ))

    def test_steps_muting(self):
        """Should mute a step"""
        support.create_project(self, 'larry')

        support.run_command('steps add first.py')

        r = support.run_command('steps mute S02-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps unmute S02-first.py')
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
        self.assertTrue(os.path.exists(os.path.join(directory, 'S02-first.py')))

        r = support.run_command('steps modify S02-first.py --name="second.py"')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertFalse(
            os.path.exists(os.path.join(directory, 'S02-first.py'))
        )
        self.assertTrue(
            os.path.exists(os.path.join(directory, 'S02-second.py'))
        )

    def test_steps_remove(self):
        """Should remove a step"""
        support.create_project(self, 'angelica')

        r = support.run_command('steps add first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S02-first.py')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps remove S02-fake.py')
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
        """Should list steps."""
        support.create_project(self, 'angelica')
        r = support.run_command('steps list')
        self.assertEqual(len(r.data['steps']), 1, Message(
            'New project should have one step to list',
            response=r
        ))

        for v in ['a.py', 'b.md', 'c.html', 'd.rst']:
            r = support.run_command('steps add "{}"'.format(v))
            self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('steps list')
        self.assertFalse(r.failed, 'should not have failed')

    def test_autocomplete(self):
        """Should autocomplete steps command."""
        support.create_project(self, 'gina')
        support.add_step(self, 'a.py')
        support.add_step(self, 'b.py')

        result = support.autocomplete('steps a')
        self.assertIn('add', result)

        result = support.autocomplete('steps modify ')
        self.assertEqual(
            len(result), 3,
            'there are three steps in {}'.format(result)
        )

        result = support.autocomplete('steps modify a.py --')
        self.assertIn('name=', result)

        result = support.autocomplete('steps modify fake.py --position=')
        self.assertEqual(
            len(result), 3,
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
        """Should function remotely."""
        support.create_project(self, 'nails')
        directory = cauldron.project.get_internal_project().source_directory

        closed_response = support.run_command('close')
        closed_response.join()
        self.assertTrue(closed_response.success, Message(
            'Expected new project to be closed',
            response=closed_response,
        ))

        test_app = server.create_test_app()

        opened_response = support.run_remote_command(
            'open "{}" --forget'.format(directory),
            app=test_app,
        )
        opened_response.join()
        self.assertTrue(opened_response.success, Message(
            'Opened Remote Project Failed',
            response=opened_response,
        ))

        added_response = support.run_remote_command(
            'steps add',
            app=test_app,
        )
        added_response.join()
        self.assertTrue(added_response.success, Message(
            'Add Step Failed',
            response=added_response,
        ))

        serialized = added_response.data['project']
        self.assertEqual(
            len(serialized['steps']),
            2,
            '{}'.format(serialized['steps'])
        )


def test_populate_list_action():
    """Should return early if action is list."""
    parser = MagicMock()
    steps_command.populate(parser, [], {'action': 'list'})
    assert parser.add_argument.not_called


def test_autocomplete_list():
    """Should return empty list if the action is list."""
    assert support.autocomplete('steps list ') == []


def test_autocomplete_list_flag():
    """Should return empty list if the action is list."""
    assert support.autocomplete('steps list -') == []


def test_autocomplete_remove_flag():
    """Should return keep flag completion."""
    assert support.autocomplete('steps remove foo.py -') == ['k', '-']


def test_autocomplete_no_match():
    """Should return empty list if nothing matched for autocomplete."""
    assert support.autocomplete('steps remove a.py b.py ,') == []


@patch('cauldron.project.get_internal_project')
def test_execute_no_project(
        get_internal_project: MagicMock,
):
    """Should fail if no project is open."""
    get_internal_project.return_value = None
    context = MagicMock(response=environ.Response())

    response = steps_command.execute(context)
    assert support.has_error_code(response, 'NO_OPEN_PROJECT')


@patch('cauldron.cli.commands.steps.actions.clean_steps')
@patch('cauldron.project.get_internal_project')
def test_execute_clean_action(
        get_internal_project: MagicMock,
        clean_steps: MagicMock,
):
    """Should carry out a steps clean action."""
    get_internal_project.return_value = MagicMock()
    context = MagicMock(response=environ.Response())

    steps_command.execute(context, action='clean')
    assert clean_steps.called


@patch('cauldron.cli.commands.steps.selection.select_step')
@patch('cauldron.project.get_internal_project')
def test_execute_select_action(
        get_internal_project: MagicMock,
        select_step: MagicMock,
):
    """Should carry out a steps selection action."""
    get_internal_project.return_value = MagicMock()
    context = MagicMock(response=environ.Response())

    steps_command.execute(context, action='select', step_name='foo.py')
    assert select_step.called


@patch('cauldron.project.get_internal_project')
def test_execute_no_step_name(
        get_internal_project: MagicMock
):
    """Should fail if step is not specified for the remove action."""
    get_internal_project.return_value = MagicMock()
    context = MagicMock(response=environ.Response())

    response = steps_command.execute(context, action='remove')
    assert support.has_error_code(response, 'NO_STEP_NAME')


@patch('cauldron.cli.commands.steps.sync.send_remote_command')
def test_execute_remote_list(
        send_remote_command: MagicMock
):
    """Should carry out a remote list command."""
    thread = MagicMock()
    thread.responses = [environ.Response().update(foo='bar')]
    send_remote_command.return_value = thread

    context = MagicMock(response=environ.Response())

    response = steps_command.execute_remote(context, action='list')
    assert response.data['foo'] == 'bar'


@patch('cauldron.cli.commands.steps.sync.comm.send_request')
def test_execute_remote_sync_failed(
        send_request: MagicMock
):
    """Should fail if sync status command does not succeed."""
    send_request.return_value = environ.Response().fail(code='FAKE').response
    context = MagicMock(response=environ.Response())

    response = steps_command.execute_remote(context, action='remove')
    assert support.has_error_code(response, 'FAKE')


@patch('cauldron.cli.commands.steps.execute')
@patch('cauldron.cli.commands.steps.project_opener.project_exists')
@patch('cauldron.cli.commands.steps.sync.comm.send_request')
def test_execute_remote_no_such_project(
        send_request: MagicMock,
        project_exists: MagicMock,
        execute: MagicMock,
):
    """Should fail if sync status command does not succeed."""
    project_exists.return_value = False
    send_request.return_value = environ.Response().update(
        remote_source_directory='foo'
    )
    context = MagicMock(response=environ.Response())

    steps_command.execute_remote(context, action='remove')
    assert execute.not_called


@patch('cauldron.cli.commands.steps.projects.Project')
@patch('cauldron.cli.commands.steps.execute')
@patch('cauldron.cli.commands.steps.project_opener.project_exists')
@patch('cauldron.cli.commands.steps.sync.comm.send_request')
def test_execute_remote_fails(
        send_request: MagicMock,
        project_exists: MagicMock,
        execute: MagicMock,
        project_constructor: MagicMock,
):
    """Should fail if local execute command does not succeed."""
    project_exists.return_value = True
    send_request.return_value = environ.Response().update(
        remote_source_directory='foo'
    )
    context = MagicMock(response=environ.Response())
    execute.return_value = environ.Response().fail(code='FAKE').response

    response = steps_command.execute_remote(context, action='remove')
    assert execute.called
    assert project_constructor.called
    assert support.has_error_code(response, 'FAKE')
