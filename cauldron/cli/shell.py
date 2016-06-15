import cmd
import json

import cauldron
from cauldron import environ
from cauldron import templating
from cauldron.cli import commands

with open(environ.paths.package('package_data.json'), 'r+') as f:
    package_data = json.load(f)


def render_intro():
    return '\n{}\n'.format(
        templating.render_template(
            'shell_introduction.txt',
            version=package_data['version']
        )
    )


class CauldronShell(cmd.Cmd):
    intro = render_intro()
    prompt = '<>: '

    def __init__(self):
        """

        """

        super(CauldronShell, self).__init__(completekey='tab')
        self.history = []

    def default(self, line: str):
        """

        :param line:
        :return:
        """

        line = line.strip()
        if len(line) < 1:
            return

        self.history.append(line)
        name, raw_args = commands.split_line(line)

        if name == 'help':
            commands.show_help()
            return

        result = commands.execute(name, raw_args)

        p = cauldron.project
        if not p or not p.internal_project or not p.internal_project.id:
            name = ''
        else:
            name = cauldron.project.internal_project.id[:20]

        self.prompt = '<{}>: '.format(name)
        return result.ended

    def do_help(self, arg):
        """

        :param arg:
        :return:
        """

        commands.show_help(arg)

    def completenames(self, text, *ignored):
        """

        :param text:
        :param ignored:
        :return:
        """

        return [
            x for x in commands.list_command_names()
            if x.startswith(text)
        ]

    def completedefault(self, text, line, begin_index, end_index):
        """

        :param text:
        :param line:
        :param begin_index:
        :param end_index:
        :return:
        """

        name, raw_args = commands.split_line(line)
        return commands.autocomplete(name, text, line, begin_index, end_index)

