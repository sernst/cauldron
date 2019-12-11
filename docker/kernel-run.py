"""
Python entrypoint for containerized use of the kernel.
"""
import argparse
import os
import textwrap

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
            It's not likely that this needs to be changed given that it
            is mapped internally inside the docker container unless using
            host networking on a linux system or the default port is used
            for something else within the container.
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
    print('[INFO]: Kernel listening internally on port {}'.format(args.port))

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

    print(textwrap.dedent(
        """
        [STARTED]: Cauldron kernel available at PORT
            where PORT is the host port that you mapped the internal
            container port {port} to with the `-p PORT:{port}` argument.
        """.format(port=args.port)
    ))
    print('\n[STARTED]: Cauldron kernel on port {}'.format(args.port))
    os.system('; '.join(commands))


if __name__ == '__main__':
    main()
