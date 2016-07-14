from cauldron import cli
from cauldron import environ
from cauldron.cli import commands
from cauldron.environ.response import Response
from cauldron.cli import parse

COMMANDS = dict()


def fetch(reload: bool = False) -> dict:
    """
    Returns a dictionary containing all of the available Cauldron commands
    currently registered. This data is cached for performance. Unless the
    reload argument is set to True, the command list will only be generated
    the first time this function is called.

    :param reload:
        Whether or not to disregard any cached command data and generate a
        new dictionary of available commands.

    :return:
        A dictionary where the keys are the name of the commands and the
        values are the modules for the command .
    """

    if len(list(COMMANDS.keys())) > 0 and not reload:
        return COMMANDS

    COMMANDS.clear()

    for key in dir(commands):
        e = getattr(commands, key)
        if e and hasattr(e, 'NAME') and hasattr(e, 'DESCRIPTION'):
            COMMANDS[e.NAME] = e

    return dict(COMMANDS.items())


def execute(
        name: str,
        raw_args: str,
        output: Response = None
) -> Response:
    """

    :return:
    """

    if not output:
        output = Response(identifier=name)
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
        return None

    if command_args is None or command_args['show_help']:
        # Overrides standard execution and instead displays the help for the
        # command
        parser.print_help()
        return None

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

    msg = []
    for key, item in fetch().items():
        if hasattr(item, 'DESCRIPTION'):
            entries[key] = cli.reformat(getattr(item, 'DESCRIPTION'))

            msg.append('[{key}]:\n   {description}'.format(
                key=key,
                description=entries[key].replace('\n', '\n   ')
            ))

    return environ.output.notify(
        kind='INFO',
        code='MODULE_DESCRIPTIONS'
    ).kernel(
        commands=entries
    ).console(
        '\n'.join(msg),
        whitespace=1
    ).get_response()


def show_help(command_name: str = None, raw_args: str = '') -> Response:
    """ Prints the basic command help to the console """

    if not environ.output:
        environ.output = Response()

    cmds = fetch()
    if command_name and command_name in cmds:
        parser, result = parse.get_parser(
            command_name,
            parse.explode_line(raw_args),
            dict()
        )

        if parser is not None:
            out = parser.format_help()
            return environ.output.notify(
                kind='INFO',
                code='COMMAND_DESSCRIPTION'
            ).kernel(
                commands=out
            ).console(
                out,
                whitespace=1
            ).get_response()

    environ.log_header('Available Commands')
    print_module_help()

    return environ.output.fail().notify(
        kind='ERROR',
        code='NO_SUCH_COMMAND',
        message='Failed to show command help for "{}"'.format(command_name)
    ).console(
        """
        For more information on the various commands, enter help on the
        specific command:

            [COMMAND] help
        """,
        whitespace_bottom=1
    ).get_response()


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
    if line.endswith(' '):
        parts.append('')

    try:
        module = cmds[command_name]
        if hasattr(module, 'autocomplete'):
            out = getattr(module, 'autocomplete')(prefix, line, parts)
            if out is not None:
                return out
    except Exception as err:
        print(err)

    return []
