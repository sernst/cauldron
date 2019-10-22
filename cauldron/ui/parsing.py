from argparse import ArgumentParser


def create_parser(
        arg_parser: ArgumentParser = None,
        shell: bool = False
) -> ArgumentParser:
    """
    Creates an argument parser populated with the arg formats for the server
    command.
    """

    parser = arg_parser or ArgumentParser()
    parser.description = 'Cauldron kernel server'

    parser.add_argument(
        '-p', '--port',
        dest='port',
        type=int,
        default=8899
    )

    parser.add_argument(
        '-n', '--name', '--host',
        dest='host',
        type=str,
        default=None
    )

    parser.add_argument(
        '--public',
        default=False,
        action='store_true'
    )

    if not shell:
        parser.add_argument(
            '-d', '--debug',
            dest='debug',
            default=False,
            action='store_true'
        )

        parser.add_argument(
            '-v', '--version',
            dest='version',
            default=False,
            action='store_true'
        )

        parser.add_argument(
            '-c', '--connect', '--connection',
            dest='connection_url'
        )

    return parser
