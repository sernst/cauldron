import cmd

from cauldron.cli import commands


class CauldronShell(cmd.Cmd):
    intro = 'Cauldron Started\nType help or ? to list commands.\n'
    prompt = '>>> '

    def __init__(self):
        super(CauldronShell, self).__init__(completekey='tab')
        self.history = []

    def execute_command(self, name: str, raw_args: str):
        args = (name, raw_args)
        self.history.append(args)
        return commands.execute(*args)

    def do_clear(self, raw_args):
        self.execute_command('clear', raw_args)

    def do_open(self, raw_args):
        self.execute_command('open', raw_args)

    def do_run(self, raw_args):
        self.execute_command('run', raw_args)

    def do_configure(self, raw_args):
        self.execute_command('configure', raw_args)

    def do_export(self, raw_args):
        self.execute_command('export', raw_args)

    def do_exit(self, raw_args):
        return self.execute_command('exit', raw_args)

    def do_help(self, arg):
        commands.show_help()
