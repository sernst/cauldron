from unittest.mock import MagicMock
import json
import os
from unittest.mock import patch

import cauldron as cd
from cauldron import environ
from cauldron.cli.commands.create import actions as create_actions
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestCreate(scaffolds.ResultsTest):
    """ """

    def test_create_no_args(self):
        """ should fail with no args """

        r = support.create_project(self, '', '', confirm=False)
        self.assertTrue(r.failed, 'should have failed')

    def test_create_no_path(self):
        """
        """

        r = support.create_project(self, 'test_create', '', confirm=False)
        self.assertTrue(r.failed, 'should have failed')

    def test_create_simple_success(self):
        """
        """

        r = support.create_project(self, 'test_create')

        self.assertFalse(
            r.failed,
            support.Message(
                'Failed to create project',
                response=r
            )
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
        """ """

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
        """
        """

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
        """

        :return:
        """

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
        """ should create libs and assets folders in project """

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
        """ should fail if directory cannot be written """

        target = 'cauldron.cli.commands.create.actions.write_project_data'
        with patch(target) as func:
            func.return_value = False
            result = support.create_project(self, 'aurelius', confirm=False)

        self.assertTrue(result.failed)

    def test_create_fail(self):
        """ should fail if directory cannot be created """

        target = '.'.join([
            'cauldron.cli.commands.create',
            'actions.create_project_directories'
        ])
        with patch(target) as func:
            func.return_value = False
            result = support.create_project(self, 'augustus', confirm=False)

        self.assertTrue(result.failed)

    def test_autocomplete_absolute_path(self):
        """ should properly autocomplete an alias """

        directory = os.path.dirname(os.path.realpath(__file__))
        result = support.autocomplete('create fake "{}"'.format(directory))
        self.assertIsNotNone(result)

    def test_autocomplete_empty(self):
        """ should properly autocomplete an alias """

        result = support.autocomplete('create')
        self.assertEqual(len(result), 0)

    def test_incomplete_alias(self):
        """ should properly autocomplete an incomplete alias """

        result = support.autocomplete('create fake @ho')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'home:')

    def test_create_project_directory(self):
        """ should abort if directory already exists """

        path = self.get_temp_path('test-create', 'project-directory-1')
        os.makedirs(path)

        response = create_actions.create_project_directories('some-name', path)
        self.assertTrue(response.success)

    def test_create_project_directory_fail(self):
        """ should fail if directory cannot be created """

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
        """ should successfully open project remotely """

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
        """ should fail when unable to write definition file """

        with patch('builtins.open') as func:
            func.side_effect = IOError('FAKE ERROR')
            response = create_actions.write_project_data('abc', {})

        self.assert_has_error_code(response, 'PROJECT_CREATE_FAILED')
