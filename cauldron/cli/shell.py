import cmd
import json

import cauldron
from cauldron import environ
from cauldron import templating
from cauldron.cli import commander
from cauldron.cli import parse


with open(environ.paths.package('settings.json'), 'r+') as f:
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
        self.last_response = None

    def default(self, line: str):
        """

        :param line:
        :return:
        """

        line = line.strip()
        if len(line) < 1:
            return

        self.history.append(line)
        name, raw_args = parse.split_line(line)

        if name == 'help':
            return commander.show_help().ended

        result = commander.execute(name, raw_args)
        if result.thread:
            result.thread.join()

        p = cauldron.project
        if not p or not p.internal_project or not p.internal_project.id:
            name = ''
        else:
            name = cauldron.project.internal_project.id[:20]

        self.prompt = '<{}>: '.format(name)
        if hasattr(result, 'ended'):
            self.last_response = result
            return result.ended
        elif hasattr(result, 'response'):
            self.last_response = result.response
            return result.response.ended
        else:
            self.last_response = None
            return result

    def do_help(self, arg):
        """

        :param arg:
        :return:
        """

        return commander.show_help(arg).ended

    def completenames(self, text, *ignored):
        """

        :param text:
        :param ignored:
        :return:
        """

        return [
            n for n in commander.fetch().keys() if n.startswith(text)
        ]

    def completedefault(self, text, line, begin_index, end_index):
        """

        :param text:
        :param line:
        :param begin_index:
        :param end_index:
        :return:
        """

        name, raw_args = parse.split_line(line)
        return commander.autocomplete(name, text, line, begin_index, end_index)

    def cmdloop(self, intro=None):
        environ.modes.add(environ.modes.INTERACTIVE)
        super(CauldronShell, self).cmdloop(intro=intro)
        environ.modes.remove(environ.modes.INTERACTIVE)