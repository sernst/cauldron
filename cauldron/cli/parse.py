import re
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ

FLAG_PATTERN = re.compile(
    '^(?P<prefix>-{1,2})(?P<name>[a-zA-Z0-9\-_]+)=?(?P<value>.*)$'
)


def split_line(line: str) -> typing.Tuple[str, str]:
    """
    Separates the raw line string into two strings: (1) the command and (2) the
    argument(s) string

    :param line:
    :return:
    """

    index = line.find(' ')
    if index == -1:
        return line.lower(), ''

    return line[:index].lower(), line[index:].strip()


def explode_line(raw: str) -> typing.List[str]:
    """

    :param raw:
    :return:
    """

    raw = re.sub('\s+', ' ', raw.strip())
    out = ['']
    breaker = ' '

    for index in range(len(raw)):
        c = raw[index]
        out[-1] += c

        if c == breaker:
            out[-1] = out[-1].strip()
            out.append('')
            breaker = ' '
        elif c == '"' and breaker == ' ':
            breaker = '"'
            continue

    return [x for x in out if len(x) > 0]


def args(
        module,
        args_str: str
) -> typing.Tuple[ArgumentParser, dict]:
    """

    :param module:
    :param args_str:
    :return:
    """

    args_list = explode_line(args_str)
    assigned_args = dict()
    parser, status = get_parser(module, args_list, assigned_args)

    if parser is None or status is 'error':
        return None, None

    for arg in args_str:
        if arg in ['?', '-?', '--?', '-h', '--h', 'help', '-help', '--help']:
            return parser, None

    def error_overload(message):
        """
        This function overloads the ArgumentParser.error function on the
        instance created in this method. The default behavior prints an
        error message to standard out and exits the program in error instead
        of raising an exception to be handled. This behavior is undesirable,
        so it gets replaced with an error function that does Cauldron's
        bidding.

        :param message:
            The error message from the parser
        """

        environ.output.fail().notify(
            kind='ERROR',
            code='INVALID_ARGUMENTS',
            message=message
        ).kernel(
            raw_args=args_str
        ).console()

    parser.error = error_overload

    parsed_args = vars(parser.parse_args(args_list))

    if environ.output.failed:
        return None, None

    out = dict()
    out.update(assigned_args)
    out.update(parsed_args)

    return parser, out


def get_parser(
        module,
        raw_args: typing.List[str],
        assigned_args: dict
) -> typing.Tuple[ArgumentParser, str]:
    """

    :param module:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    description = None
    if hasattr(module, 'DESCRIPTION'):
        description = getattr(module, 'DESCRIPTION')

    parser = ArgumentParser(
        prog=module.NAME,
        add_help=False,
        description=description
    )

    parser.add_argument(
        '-h', '--help',
        dest='show_help',
        action='store_true',
        default=False,
        help=cli.reformat(
            """
            Print this help information instead of running the command
            """
        )
    )

    if not hasattr(module, 'populate'):
        return parser, None

    try:
        getattr(module, 'populate')(parser, raw_args, assigned_args)
        if environ.output.failed:
            return parser, 'error'
        return parser, None
    except Exception as err:
        environ.output.fail().notify(
            kind='ERROR',
            code='ARGS_PARSE_ERROR',
            message='Unable to parse command arguments'
        ).kernel(
            name=module.NAME,
            error=str(err)
        ).console()
        return parser, 'error'
