import json
import os
from unittest.mock import MagicMock
from unittest.mock import patch

import cauldron as cd
from cauldron import environ
from cauldron.cli.commands.create import actions as create_actions
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestCreate(scaffolds.ResultsTest):
    """Test suite for the 'create' CLI command."""

    def test_create_no_args(self):
        """Should fail with no args."""
        r = support.create_project(self, '', '', confirm=False)
        self.assertTrue(r.failed, 'Expect command failure')

    def test_create_no_path(self):
        """Should fail with no path."""
        r = support.create_project(self, 'test_create', '', confirm=False)
        self.assertTrue(r.failed, 'Expect command failure')

    def test_create_simple_success(self):
        """Should succeed to create a project."""
        r = support.create_project(self, 'test_create')

        self.assertFalse(
            r.failed,
            support.Message('Failed to create project', response=r)
        )

        path = os.path.join(r.data['source_directory'], 'cauldron.json')
        self.assertTrue(
            os.path.exists(path),
            support.Message(
                'No project found',
                'Missing cauldron.json file that should exist when a new',
                'project is created',
                response=r,
                path=path
            )
        )

    def test_create_twice(self):
        """Should fail while trying to create while another project is open."""
        r1 = support.create_project(self, 'test_create')
        r1.identifier = 'First {}'.format(r1.identifier)

        r2 = support.create_project(self, 'test_create', confirm=False)
        r2.identifier = 'Second {}'.format(r2.identifier)

        self.assertTrue(
            r2.failed,
            support.Message(
                'No second project',
                'It should not be possible to create a second project in the',
                'same location',
                response=r2
            )
        )

    def test_create_full_success(self):
        """Should create a new project."""
        r = support.create_project(
            self,
            'test_create',
            title='This is a test',
            summary='More important information goes in this spot',
            author='Kermit the Frog'
        )

        self.assertFalse(
            r.failed,
            'Failed to create project\n:{}'.format(r.echo())
        )

        self.assertTrue(
            os.path.exists(
                os.path.join(r.data['source_directory'], 'cauldron.json')
            ),
            'Missing cauldron.json in new project folder\n:{}'.format(r.echo())
        )

    def test_autocomplete(self):
        """Should autocomplete the create command."""
        alias = 'ex'
        path = environ.paths.resources('examples')
        support.run_command(
            'alias add "{}" "{}" --temporary'.format(alias, path)
        )

        result = support.autocomplete('create my_project @home:')
        self.assertIsNotNone(
            result,
            support.Message(
                'autocomplete result should not be None',
                result=result
            )
        )

        # Get all directories in the examples folder
        items = [(e, os.path.join(path, e)) for e in os.listdir(path)]
        items = [e for e in items if os.path.isdir(e[1])]

        result = support.autocomplete('create my_project @ex:')
        self.assertEqual(
            len(result), len(items),
            support.Message(
                'should autocomplete from the examples folder',
                result=result,
                items=items
            )
        )

        hellos = [e for e in items if e[0].startswith('hell')]
        result = support.autocomplete('create my_project @ex:hell')
        self.assertEqual(
            len(result), len(hellos),
            support.Message(
                'should autocomplete examples that start with "hell"',
                result=result,
                items=items
            )
        )

    def test_folders(self):
        """Should create libs and assets folders in project."""
        libs_folder = 'libs_folder'
        assets_folder = 'assets_folder'

        result = support.create_project(
            self,
            'marcus',
            libs=libs_folder,
            assets=assets_folder
        )
        self.assertFalse(result.failed)

        project = cd.project.get_internal_project()

        items = os.listdir(project.source_directory)

        self.assertIn(libs_folder, items)
        self.assertIn(assets_folder, items)

        self.assertIn(libs_folder, project.settings.fetch('library_folders'))
        self.assertIn(assets_folder, project.settings.fetch('asset_folders'))

        with open(project.source_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(libs_folder, data['library_folders'][0])
        self.assertEqual(assets_folder, data['asset_folders'][0])

    def test_write_fail(self):
        """Should fail if directory cannot be written."""
        target = 'cauldron.cli.commands.create.actions.write_project_data'
        with patch(target) as func:
            func.return_value = False
            result = support.create_project(self, 'aurelius', confirm=False)

        self.assertTrue(result.failed)

    def test_create_fail(self):
        """Should fail if directory cannot be created."""
        target = '.'.join([
            'cauldron.cli.commands.create',
            'actions.create_project_directories'
        ])
        with patch(target) as func:
            func.return_value = False
            result = support.create_project(self, 'augustus', confirm=False)

        self.assertTrue(result.failed)

    def test_autocomplete_absolute_path(self):
        """Should properly autocomplete an alias."""
        directory = os.path.dirname(os.path.realpath(__file__))
        result = support.autocomplete('create fake "{}"'.format(directory))
        self.assertIsNotNone(result)

    def test_autocomplete_empty(self):
        """Should properly autocomplete an alias."""
        result = support.autocomplete('create')
        self.assertEqual(len(result), 0)

    def test_incomplete_alias(self):
        """Should properly autocomplete an incomplete alias."""
        result = support.autocomplete('create fake @ho')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'home:')

    def test_create_project_directory(self):
        """Should abort if directory already exists."""
        path = self.get_temp_path('test-create', 'project-directory-1')
        os.makedirs(path)

        response = create_actions.create_project_directories('some-name', path)
        self.assertTrue(response.success)

    def test_create_project_directory_fail(self):
        """Should fail if directory cannot be created."""
        path = self.get_temp_path('test-create', 'project-directory-2')

        with patch('os.makedirs') as make_dirs:
            make_dirs.side_effect = IOError('Fake Error')
            response = create_actions.create_project_directories(
                'some-name',
                path
            )
        self.assertFalse(response.success)

    @patch('cauldron.cli.commands.open.remote.sync_open')
    def test_remote(self, sync_open: MagicMock):
        """Should successfully open project remotely."""
        sync_open.return_value = environ.Response()

        response = support.create_project(
            self,
            'tester',
            confirm=False,
            remote_connection=environ.RemoteConnection(True, 'something.url')
        )

        self.assertTrue(response.success)
        self.assertGreater(sync_open.call_count, 0)

    def test_write_project_data_failure(self):
        """Should fail when unable to write definition file."""
        with patch('builtins.open') as func:
            func.side_effect = IOError('FAKE ERROR')
            response = create_actions.write_project_data('abc', {})

        self.assert_has_error_code(response, 'PROJECT_CREATE_FAILED')

    @patch('cauldron.cli.commands.create.create_actions.create_first_step')
    @patch('cauldron.cli.commands.create.create_actions.write_project_data')
    def test_fail_create_step(
            self,
            write_project_data: MagicMock,
            create_first_step: MagicMock,
    ):
        """Should fail when unable to create default step."""
        create_first_step.return_value = environ.Response().fail(code='FOO')
        response = support.create_project(
            tester=self,
            name='test_fail_create_step',
            confirm=False,
        )

        assert support.has_error_code(response, 'FOO'), """
            Expect create to fail on 'create_first_step' call.
            """
        assert 0 == write_project_data.call_count, """
            Expect create process to abort before writing project data.
            """

    @patch('cauldron.cli.commands.create.create_actions.create_first_step')
    @patch('cauldron.cli.commands.create.create_actions.write_project_data')
    def test_fail_write_project(
            self,
            write_project_data: MagicMock,
            create_first_step: MagicMock,
    ):
        """Should fail when unable to create default step."""
        create_first_step.return_value = environ.Response().update(
            step_name='foo'
        )
        write_project_data.return_value = environ.Response().fail(code='FOO')

        response = support.create_project(
            tester=self,
            name='test_fail_write_project_data',
            confirm=False,
        )

        assert support.has_error_code(response, 'FOO'), """
            Expect create to fail on 'write_project_data' call.
            """
        assert 1 == create_first_step.call_count, """
            Expect create process to create first default step before
            failing to write project data.
            """


@patch('cauldron.cli.commands.create.actions.open')
def test_create_first_step(opener: MagicMock):
    """Should create first step for the new project."""
    opener = support.populate_open_mock(opener)

    response = create_actions.create_first_step(
        project_directory=os.path.dirname(__file__),
        project_name='foo'
    )

    assert response.success, 'Expect action to succeed.'
    assert 1 == opener.mocked_file.write.call_count, """
        Expect the step contents to be written to a file.
        """


@patch('cauldron.cli.commands.create.actions.open')
def test_create_first_step_fail(opener: MagicMock):
    """Should fail to create first step for the new project."""
    opener = support.populate_open_mock(opener)
    opener.mocked_file.write.side_effect = ValueError

    response = create_actions.create_first_step(
        project_directory=os.path.dirname(__file__),
        project_name='foo'
    )

    assert response.failed, 'Expect action to fail.'
    assert support.has_error_code(response, 'PROJECT_CREATE_FAILED')
    assert 1 == opener.mocked_file.write.call_count, """
        Expect an attempt to write the step to disk.
        """
