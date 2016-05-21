import cmd
# import readline

import cauldron
from cauldron import templating
from cauldron.cli import commands

# readline.set_completer_delims(' \t\n')


class CauldronShell(cmd.Cmd):
    intro = '\n{}\n'.format(
        templating.render_template('shell_introduction.txt')
    )
    prompt = '<>: '

    def __init__(self):
        super(CauldronShell, self).__init__(completekey='tab')
        self.history = []

    def default(self, line: str):
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
        if not p or not p.internal_project or not p.internal_project.title:
            name = ''
        else:
            name = cauldron.project.internal_project.title[:20]

        self.prompt = '<{}>: '.format(name)
        return result

    def do_help(self, arg):
        commands.show_help(arg)

    def completenames(self, text, *ignored):
        return [
            x for x in commands.list_command_names()
            if x.startswith(text)
        ]

    def completedefault(self, text, line, begin_index, end_index):
        name, raw_args = commands.split_line(line)
        return commands.autocomplete(name, text, line, begin_index, end_index)

