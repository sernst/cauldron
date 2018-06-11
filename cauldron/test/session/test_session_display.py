import os

import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSessionDisplay(scaffolds.ResultsTest):

    def test_html(self):
        """ should add an html div tag to the display """

        support.create_project(self, 'helo')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.html("<div></div>")'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_svg(self):
        """ should add an svg tag to the display """

        support.create_project(self, 'athena')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.svg("<svg></svg>", "filename")'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_status(self):
        """ should update status display """

        support.create_project(self, 'husker')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.status(',
            '    "Some Message",',
            '    0.8,',
            '    "Section Message",',
            '    0.2',
            ')'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_listing(self):
        """ should add list to display """

        support.create_project(self, 'apollo')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.listing([1, 2, 3, 4])'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_list_grid(self):
        """ should add list grid to display """

        support.create_project(self, 'apollo-grid')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.list_grid([1, 2, 3, 4])'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_whitespace(self):
        """ should add list to display """

        support.create_project(self, 'hera')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.whitespace(4)'
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_jinja(self):
        """ should add jinja template to display """

        support.create_project(self, 'starbuck')

        project = cauldron.project.get_internal_project()

        jinja_path = os.path.join(
            project.source_directory,
            'template.html'
        )

        with open(jinja_path, 'w') as fp:
            fp.write('<div>Hello {{ name }}</div>')

        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.jinja("{}", name="starbuck")'.format(
                jinja_path.replace('\\', '\\\\')
            )
        ])

        support.add_step(self, contents=step_contents)

        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')

    def test_elapsed(self):
        """Should render elapsed time"""
        support.create_project(self, 'test_elapsed')
        step_contents = '\n'.join([
            'import cauldron as cd',
            'cd.display.elapsed()'
        ])
        support.add_step(self, contents=step_contents)
        r = support.run_command('run')
        self.assertFalse(r.failed, 'should not have failed')
