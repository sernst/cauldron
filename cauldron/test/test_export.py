import os

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestExport(scaffolds.ResultsTest):
    """

    """

    def test_exporting(self):
        """
        """

        support.run_command('open @examples:pyplot')
        support.run_command('run')

        path = self.get_temp_path('exporting')
        folder_name = 'exported-results'
        r = support.run_command('export "{}" --directory="{}"'.format(
            path, folder_name
        ))
        self.assertFalse(r.failed, 'should not have failed')

        directory = os.path.join(path, folder_name)
        self.assertTrue(
            os.path.exists(directory) and os.path.isdir(directory)
        )

        support.run_command('close')
