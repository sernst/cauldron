import os

import cauldron as cd
from cauldron import environ
from cauldron.session import projects
from cauldron.test.support import scaffolds
from cauldron.test import support
from cauldron.session.caching import SharedCache
from cauldron.session.projects import definitions

class TestProject(scaffolds.ResultsTest):
    """

    """

    def test_file_source_path(self):
        """A file source directory should be a directory"""

        support.create_project(self, 'lupin')
        project = cd.project.get_internal_project()

        p = projects.Project(project.source_path)
        self.assertTrue(os.path.isdir(p.source_directory))
        self.assertEqual(p.source_directory, project.source_directory)

    def test_shared_dict(self):
        """A dict shared argument should be converted into a SharedCache"""

        support.create_project(self, 'tonks')
        project = cd.project.get_internal_project()

        shared_data = {'a': 1, 'b': True}
        p = projects.Project(project.source_directory, shared=shared_data)

        self.assertIsInstance(p.shared, SharedCache)

        for key, value in shared_data.items():
            self.assertEqual(p.shared.fetch(key), value)

    def test_title(self):
        """Project title should be readable and writable"""

        support.create_project(self, 'sirius')
        project = cd.project.get_internal_project()

        title = 'My Title'
        project.title = title
        self.assertEqual(title, project.title)

    def test_results_path(self):
        """Results path should always be valid"""

        def assert_valid_path(test: str) -> bool:
            return self.assertTrue(
                test is not None and
                len(test) > 0
            )

        support.create_project(self, 'dudley')
        project = cd.project.get_internal_project()

        project._results_path = None
        assert_valid_path(project.results_path)

        results_directory = environ.configs.fetch('results_directory')
        environ.configs.put(results_directory=None, persists=False)

        assert_valid_path(project.results_path)

        project.settings.put('path_results', os.path.realpath('.'))
        assert_valid_path(project.results_path)

        project.settings.put('path_results', None)
        assert_valid_path(project.results_path)

        environ.configs.put(results_directory=results_directory, persists=False)

    def test_has_no_error(self):
        """Should not have an error"""

        support.create_project(self, 'vernon')
        project = cd.project.get_internal_project()

        self.assertFalse(project.has_error, 'error on project without steps')

        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        support.run_command('run')

        self.assertFalse(project.has_error, 'error after running steps')

    def test_has_error(self):
        """Should have error if step raises an error when run"""

        support.create_project(self, 'petunia')
        project = cd.project.get_internal_project()

        support.add_step(self, contents='raise Exception("test")')
        support.run_command('run')

        self.assertTrue(project.has_error, 'step should have errored')

    def test_get_no_step(self):
        """Should not find a step that doesn't exist"""

        support.create_project(self, 'luna')
        project = cd.project.get_internal_project()

        support.add_step(self)
        support.add_step(self)

        self.assertIsNone(project.get_step('NoSuchStep'))
        self.assertIsNone(project.get_step_by_reference_id('NoSuchStep'))
        self.assertIsNone(project.index_of_step('NoSuchStep'))

    def test_no_such_settings(self):
        """Error when no project settings file exists"""

        with self.assertRaises(FileNotFoundError):
            definitions.load_project_definition(
                os.path.dirname(os.path.realpath(__file__))
            )
