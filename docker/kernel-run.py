"""
Python entrypoint for containerized use of the kernel.
"""
import argparse
import os
import shutil
import textwrap
import typing

from cauldron import templating
from cauldron.ui import launcher


def parse() -> argparse.Namespace:
    """
    Parse arguments from the command line.
    """
    with open('/launch/kernel-description.txt') as f:
        description = f.read()

    parser = argparse.ArgumentParser(
        prog='cauldron-kernel',
        description=description,
    )
    parser.add_argument('--debug', action='store_true', help=textwrap.dedent(
        """
        Executes the Cauldron kernel in debug mode for development use. Should
        not be used otherwise.
        """
    ))
    parser.add_argument(
        '--port',
        type=int,
        default=5010,
        help=textwrap.dedent(
            """
            Specifies the port that the kernel should be made available on.
            """
        )
    )
    return parser.parse_args()


def main():
    """Parse arguments into environment configuration."""
    templating.render_splash()

    args = parse()

    gunicorn_port = launcher.find_open_port(
        '0.0.0.0',
        [p for p in range(8000, 9000) if p != args.port]
    )

    envs = {
        'CAULDRON_INITIAL_DIRECTORY': '/notebooks',
        'CAULDRON_SERVER_PORT': str(gunicorn_port),
        'CAULDRON_LISTEN_PORT': str(args.port),
    }

    with open('/launch/kernel-nginx.rendered.conf', 'w') as f:
        f.write(templating.render_file(
            '/launch/kernel-nginx.conf',
            gunicorn_port=gunicorn_port,
            listen_port=args.port,
            debug=args.debug,
        ))
    os.system('nginx -c /launch/kernel-nginx.rendered.conf')

    print('[INFO]: Internal proxy port {}'.format(gunicorn_port))
    print('[INFO]: Kernel listening on port {}'.format(args.port))

    commands = [
        'export {}="{}"'.format(key, value)
        for key, value in envs.items()
        if value
    ]

    commands.append(' '.join([
        'gunicorn',
        '--name=cauldron-ui',
        '--log-level={}'.format('debug' if args.debug else 'warning'),
        '--bind=0.0.0.0:{}'.format(gunicorn_port),
        '-w', '1',
        '--chdir', '/launch',
        'kernel'
    ]))

    print('\n[STARTED]: Cauldron kernel on port {}'.format(args.port))
    os.system('; '.join(commands))


if __name__ == '__main__':
    main()
