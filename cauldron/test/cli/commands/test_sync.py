import os
import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSync(scaffolds.ResultsTest):
    """ """

    def test_sync_project(self):
        """ should synchronize local files to remote location """

        support.run_remote_command('open @examples:hello_cauldron')
        response = support.run_remote_command('sync')
        self.assertTrue(response.success)

        project = cauldron.project.internal_project
        self.trace(project.remote_source_directory)
        self.trace(project.source_directory)

        remote_files = sorted(os.listdir(project.remote_source_directory))
        local_files = sorted(os.listdir(project.source_directory))

        self.assertEqual(remote_files, local_files)

    def test_sync_no_connection(self):
        """ should fail if no remote connection is active """

        response = support.run_command('sync')
        self.assert_has_error_code(response, 'NO_REMOTE_CONNECTION')
