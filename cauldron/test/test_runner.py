from cauldron import cli
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRunner(scaffolds.ResultsTest):
    """

    """

    def test_exception(self):
        """
        """

        support.initialize_project(self, 'brad')
        support.add_step(
            self, 'brad_one.py', cli.reformat(
                """
                import cauldron as cd

                a = dict(
                    one=1,
                    two=['1', '2'],
                    three={'a': True, 'b': False, 'c': True}
                )

                cd.display.inspect(a)
                cd.shared.a = a
                cd.display.workspace()

                """
            )
        )
        support.add_step(self, 'brad_two.py', "1 + 's'")

        r = support.run_command('run .')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('run .')
        self.assertTrue(r.failed, 'should have failed')

        support.run_command('close')



