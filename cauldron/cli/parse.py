import re
import typing
from argparse import ArgumentParser
from collections import namedtuple

from cauldron import cli
from cauldron.environ import Response

FLAG_PATTERN = re.compile(
    r'^(?P<prefix>-{1,2})(?P<name>[a-zA-Z0-9\-_]+)=?(?P<value>.*)$'
)

ARGS_RESPONSE_NT = namedtuple(
    'ArgsResponse_nt',
    ['parser', 'args', 'response']
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

    raw = re.sub(r'\s+', ' ', raw.strip())
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
) -> ARGS_RESPONSE_NT:
    """

    :param module:
    :param args_str:
    :return:
    """

    args_list = explode_line(args_str)
    assigned_args = dict()
    parser, response = get_parser(module, args_list, assigned_args)

    if parser is None or response.failed:
        return ARGS_RESPONSE_NT(None, None, response)

    for arg in args_str:
        if arg in ['?', '-?', '--?', '-h', '--h', 'help', '-help', '--help']:
            return ARGS_RESPONSE_NT(parser, None, response)

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

        response.fail(
            code='INVALID_ARGUMENTS',
            message=message
        ).kernel(
            raw_args=args_str
        ).console(
            whitespace=1
        )

    parser.error = error_overload

    parsed_args = vars(parser.parse_args(args_list))

    if response.failed:
        return ARGS_RESPONSE_NT(None, None, response)

    args_result = dict()
    args_result.update(assigned_args)
    args_result.update(parsed_args)

    # Clean the argument values of quote characters and hanging whitespace

    def clean_arguments(item):
        if isinstance(item[1], str):
            return item[0], item[1].strip('" \t')
        return item

    return ARGS_RESPONSE_NT(
        parser,
        dict(map(clean_arguments, args_result.items())),
        response
    )


def get_parser(
        target_module,
        raw_args: typing.List[str],
        assigned_args: dict
) -> typing.Tuple[ArgumentParser, Response]:
    """

    :param target_module:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    response = Response()

    description = None
    if hasattr(target_module, 'DESCRIPTION'):
        description = getattr(target_module, 'DESCRIPTION')

    parser = ArgumentParser(
        prog=target_module.NAME,
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

    if not hasattr(target_module, 'populate'):
        return parser, response

    try:
        getattr(target_module, 'populate')(parser, raw_args, assigned_args)
    except Exception as err:
        response.fail(
            code='ARGS_PARSE_ERROR',
            message='Unable to parse command arguments',
            error=err,
            name=target_module.NAME
        ).console(whitespace=1)

    return parser, response
