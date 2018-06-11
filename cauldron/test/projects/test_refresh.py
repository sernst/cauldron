import json

import cauldron as cd
from cauldron.session import projects
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRefresh(scaffolds.ResultsTest):
    """ """

    @classmethod
    def read_project_file(cls, project: projects.Project = None) -> dict:
        """
        Reads the project's data file from disk
        """

        target_project = (
            project
            if project else
            cd.project.get_internal_project()
        )

        with open(target_project.source_path, 'r') as f:
            return json.load(f)

    @classmethod
    def write_project_file(cls, data: dict, project: projects.Project = None):
        """
        Overwrites the existing project data file with the specified data
        """
        target_project = (
            project
            if project else
            cd.project.get_internal_project()
        )

        with open(target_project.source_path, 'w+') as f:
            json.dump(data, f)

        return target_project.source_path

    def test_modified_file(self):
        """
        The project should refresh without error after the cauldron project
        file is modified by external means
        """

        step_name = 'S01-FAKE.py'

        support.create_project(self, 'draco')

        project_data = self.read_project_file()
        project_data['steps'].append(step_name)
        self.write_project_file(project_data)

        project = cd.project.get_internal_project()
        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertEqual(len(project.steps), 1)
        self.assertEqual(project.steps[0].definition.name, step_name)

    def test_custom_results_path(self):
        """
        Project should update with a results path that matches the source path
        """

        support.create_project(self, 'lucius')

        project = cd.project.get_internal_project()
        project_data = self.read_project_file()
        project_data['path_results'] = project.source_directory
        self.write_project_file(project_data)

        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertEqual(project.source_directory, project.results_path)

    def test_modified_same_steps(self):
        """
        The project should refresh without error after the cauldron project
        file is modified by external means
        """

        support.create_project(self, 'dracon')

        project_data = self.read_project_file()
        project_data['change'] = True
        self.write_project_file(project_data)

        project = cd.project.get_internal_project()
        self.assertTrue(project.refresh(force=True), 'should have refreshed')
        self.assertEqual(len(project.steps), 0)

    def test_update_not_modified(self):
        """ should abort refresh if updated file is identical to previous """

        support.create_project(self, 'dracon')

        project_data = self.read_project_file()
        self.write_project_file(project_data)

        project = cd.project.get_internal_project()
        self.assertFalse(project.refresh(), 'should not have refreshed')
