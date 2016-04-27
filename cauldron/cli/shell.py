import cmd
import readline

from cauldron.cli import commands

# readline.set_completer_delims(' \t\n')


class CauldronShell(cmd.Cmd):
    intro = 'Cauldron Started\nType help or ? to list commands.\n'
    prompt = '>>> '

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

        return commands.execute(name, raw_args)

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

