from argparse import ArgumentParser

from cauldron.cli.server import run as server_run


def add_kernel_action(sub_parser: ArgumentParser) -> ArgumentParser:
    """Populates the sub parser with the kernel/server arguments"""
    return server_run.create_parser(sub_parser)


def add_shell_action(sub_parser: ArgumentParser) -> ArgumentParser:
    """Populates the sub parser with the shell arguments"""

    sub_parser.add_argument(
        '-p', '--project',
        dest='project_directory',
        type=str,
        default=None
    )

    sub_parser.add_argument(
        '-l', '--log',
        dest='logging_path',
        type=str,
        default=None
    )

    sub_parser.add_argument(
        '-o', '--output',
        dest='output_directory',
        type=str,
        default=None
    )

    sub_parser.add_argument(
        '-s', '--shared',
        dest='shared_data_path',
        type=str,
        default=None
    )

    return sub_parser


def parse(args: list = None) -> dict:
    """
    Parses the command line arguments and returns a dictionary containing the
    results.
    
    :param args:
        The command line arguments to parse. If None, the system command line
        arguments will be used instead.
    """

    parser = ArgumentParser(description='Cauldron command')
    parser.add_argument(
        'command',
        nargs='?',
        default='shell',
        help='The Cauldron command action to execute'
    )

    parser.add_argument(
        '-v', '--version',
        dest='show_version_info',
        default=False,
        action='store_true',
        help='show Cauldron version and exit'
    )

    sub_parsers = parser.add_subparsers(
        dest='command',
        title='Sub-Command Actions',
        description='The actions you can execute with the cauldron command',
    )

    sub_parsers.add_parser('shell', aliases=['version'])
    add_shell_action(sub_parsers.add_parser('shell'))
    add_kernel_action(sub_parsers.add_parser('kernel', aliases=['serve']))

    arguments = vars(parser.parse_args(args=args))
    arguments['parser'] = parser
    return arguments
