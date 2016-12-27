import json
import sys

import cauldron as cd
from cauldron.session import projects
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRefresh(scaffolds.ResultsTest):
    """

    """

    @classmethod
    def read_project_file(cls, project: projects.Project = None) -> dict:
        """
        Reads the project's data file from disk
        """

        target_project = project if project else cd.project.internal_project

        with open(target_project.source_path, 'r+') as f:
            return json.load(f)

    @classmethod
    def write_project_file(cls, data: dict, project: projects.Project = None):
        """
        Overwrites the existing project data file with the specified data
        """

        target_project = project if project else cd.project.internal_project

        with open(target_project.source_path, 'w+') as f:
            json.dump(data, f)

        return target_project.source_path

    def test_modified_file(self):
        """
        The project should refresh without error after the cauldron project
        file is modified by external means
        """

        STEP_NAME = 'S01-FAKE.py'

        support.create_project(self, 'draco')

        project_data = self.read_project_file()
        project_data['steps'].append(STEP_NAME)
        self.write_project_file(project_data)

        project = cd.project.internal_project
        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertEqual(len(project.steps), 1)
        self.assertEqual(project.steps[0].definition.name, STEP_NAME)

        support.run_command('close')

    def test_custom_results_path(self):
        """
        Project should update with a results path that matches the source path
        """

        support.run_command('close')
        support.create_project(self, 'lucius')

        project = cd.project.internal_project
        project_data = self.read_project_file()
        project_data['results_path'] = project.source_directory
        self.write_project_file(project_data)

        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertEqual(project.source_directory, project.results_path)

        support.run_command('close')

    def test_add_python_path(self):
        """
        Project should recognize the additional python path
        """

        support.create_project(self, 'cassie')

        project = cd.project.internal_project
        project_data = self.read_project_file()
        project_data['python_paths'] = project.source_directory
        self.write_project_file(project_data)

        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertIn(project.source_directory, sys.path)

        sys.path.remove(project.source_directory)

        support.run_command('close')
