from unittest.mock import patch
import string

import cauldron
from cauldron.cli import commander
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestPrinting(scaffolds.ResultsTest):

    def test_slow_printing(self):
        """Should not repeat print statements during slow running steps"""
        response = support.create_project(self, 'duluth')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        code = '\n'.join([
            'import time',
            'for letter in "BCFHMNOPRSTUVWX":',
            '    print("{}AT".format(letter))',
            '    time.sleep(0.5)'
        ])

        support.add_step(self, contents=code)
        response = commander.execute('run', '-f')
        response.thread.join(2)

        step = cauldron.project.get_internal_project().steps[0]
        dom = step.dumps()
        self.assertEqual(dom.count('BAT'), 1, 'first check failed')

        response.thread.join(1)
        dom = step.dumps()
        self.assertEqual(dom.count('BAT'), 1, 'second check failed')

        response.thread.join()
        dom = step.dumps()
        self.assertEqual(dom.count('BAT'), 1, 'third check failed')
        self.assertLess(dom.count('SAT'), 2, 'fourth check failed')

    def test_print_solo(self):
        """ should properly print in a step that does nothing but print """
        response = support.create_project(self, 'minneapolis')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        print_string = string.ascii_lowercase

        code = '\n'.join([
            'values = [x ** 2 for x in range(100)]',
            'print("{}")'.format(print_string)
        ])

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertFalse(
            response.failed,
            Message('should have run step', response=response)
        )

        project = cauldron.project.get_internal_project()
        dom = project.steps[0].dom  # type: str

        self.assertEqual(
            dom.count(print_string),
            2,
            'should have printed ascii lowercase'
        )

    def test_print_start(self):
        """ should properly print at the beginning of a step """

        response = support.create_project(self, 'chicago')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        print_string = string.ascii_lowercase

        code = '\n'.join([
            'import cauldron as cd',
            'print("{}")'.format(print_string),
            'cd.display.text("Hello World")'
        ])

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertFalse(
            response.failed,
            Message('should have run step', response=response)
        )

        project = cauldron.project.get_internal_project()
        dom = project.steps[0].dom  # type: str

        self.assertEqual(
            dom.count(print_string),
            2,
            'should have printed ascii lowercase'
        )

    def test_print_end(self):
        """ should properly print at the end of step """

        response = support.create_project(self, 'madison')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        print_string = string.ascii_lowercase

        code = '\n'.join([
            'import cauldron as cd',
            'cd.display.text("Hello World")',
            'print("{}")'.format(print_string)
        ])

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertFalse(
            response.failed,
            Message('should have run step', response=response)
        )

        project = cauldron.project.get_internal_project()
        dom = project.steps[0].dom  # type: str

        self.assertEqual(
            dom.count(print_string),
            2,
            'should have printed ascii lowercase'
        )

    def test_print_multiple(self):
        """ should properly print multiple times within a step """

        response = support.create_project(self, 'omaha')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        code = '\n'.join([
            'import cauldron as cd',
            'import string',
            'print(string.ascii_lowercase)',
            'cd.display.text("Hello World")',
            'print(string.ascii_uppercase)',
            'print(string.hexdigits)'
        ])

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertFalse(
            response.failed,
            Message('should have run step', response=response)
        )

        project = cauldron.project.get_internal_project()
        dom = project.steps[0].dom  # type: str

        self.assertEqual(
            dom.count(string.ascii_lowercase),
            1,
            'should have printed ascii lowercase'
        )

        self.assertEqual(
            dom.count(string.ascii_uppercase),
            1,
            'should have printed ascii uppercase'
        )

        self.assertEqual(
            dom.count(string.hexdigits),
            1,
            'should have printed hex digits'
        )
