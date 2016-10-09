import os

import cauldron
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestBatcher(scaffolds.ResultsTest):


    def run_project(self, project_id: str, project_directory: str):
        directory = self.get_temp_path(project_id)
        output_directory = os.path.join(directory, 'test', 'results')
        logging_path = os.path.join(directory, 'logging', 'test.log')

        response = cauldron.run_project(
            project_directory=project_directory,
            output_directory=output_directory,
            logging_path=logging_path
        )
 
        self.assertFalse(response.failed, Message(
            'Failed to run project',
            response=response
        ))
        self.assertTrue(os.path.exists(output_directory))
        self.assertTrue(os.path.exists(os.path.join(output_directory, 'display.html')))
        self.assertTrue(os.path.exists(logging_path))
        self.assertTrue(os.path.getsize(logging_path) > 0)

    def test_run_project(self):
        self.run_project('hello-cauldron', '@examples:hello_cauldron')

    def test_run_pyplot_project(self):
        self.run_project('hello-cauldron', '@examples:pyplot')
