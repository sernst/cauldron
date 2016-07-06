from cauldron import cli
from cauldron import environ
from cauldron.cli import commands
from cauldron.environ.response import Response
from cauldron.cli import parse

COMMANDS = dict()


def fetch(reload: bool = False) -> dict:
    """

    :param reload:

    :return:
    """

    if len(list(COMMANDS.keys())) > 0 and not reload:
        return COMMANDS

    COMMANDS.clear()

    for key in dir(commands):
        e = getattr(commands, key)
        if e and hasattr(e, 'NAME') and hasattr(e, 'DESCRIPTION'):
            COMMANDS[e.NAME] = e

    return COMMANDS


def execute(
        name: str,
        raw_args: str,
        output: Response = None
) -> Response:
    """

    :return:
    """

    if not output:
        output = Response()
    environ.output = output

    module = fetch().get(name)
    if module is None:
        return environ.output.fail().notify(
            kind='ERROR',
            code='NO_SUCH_COMMAND'
        ).kernel(
            name=name
        ).console(
            """
            "{name}" is not a recognized command. For a list of available
            commands enter help or ?.
            """.format(name=name)
        )

    parser, command_args = parse.args(module, raw_args)

    if parser is None:
        # The parse failed and the execution should be aborted
        return

    if command_args is None or command_args['show_help']:
        # Overrides standard execution and instead displays the help for the
        # command
        parser.print_help()
        return

    del command_args['show_help']

    module.execute(parser=parser, **command_args)
    environ.output = None

    return output


def print_module_help():
    """

    :return:
    """

    environ.log_blanks()
    entries = dict()

    for key, item in fetch().items():
        if hasattr(item, 'DESCRIPTION'):
            entries[key] = cli.reformat(getattr(item, 'DESCRIPTION'))

            msg = '[{key}]:\n   {description}'.format(
                key=key,
                description=entries[key].replace('\n', '\n   ')
            )

            environ.log(msg)

    environ.output.notify(
        kind='INFO',
        code='MODULE_DESCRIPTIONS'
    ).kernel(
        commands=entries
    )


def show_help(command_name: str = None, raw_args: str = '') -> Response:
    """ Prints the basic command help to the console """

    if not environ.output:
        environ.output = Response()

    cmds = fetch()
    if command_name and command_name in cmds:
        parser = parse.get_parser(
            command_name,
            parse.explode_line(raw_args)
        )

        if parser is not None:
            parser.print_help()
            return

    environ.log_header('Available Commands')
    print_module_help()

    environ.log(
        """
        For more information on the various commands, enter help on the
        specific command:

            [COMMAND] help
        """,
        whitespace_bottom=1
    )

    return environ.output


def autocomplete(
        command_name: str,
        prefix: str,
        line: str,
        begin_index: int,
        end_index: int
):
    """

    :param command_name:
    :param prefix:
    :param line:
    :param begin_index:
    :param end_index:
    :return:
    """

    cmds = fetch()
    if command_name not in cmds:
        return []

    parts = parse.explode_line(line)[1:]

    try:
        module = cmds[command_name]
        if hasattr(module, 'autocomplete'):
            out = getattr(module, 'autocomplete')(prefix, line, parts)
            if out is not None:
                return out
    except Exception as err:
        print(err)

    return []
