"""
Python entrypoint for containerized use of the ui.
"""
import argparse
import os
import shutil
import textwrap
import typing

from cauldron import templating
from cauldron.ui import launcher


def _open_remote_connection(
        args: argparse.Namespace
) -> typing.Optional[str]:
    """..."""
    if not args.remote:
        return args.connection_url

    ssh_directory = '/root/.ssh'
    if os.path.exists('/host_ssh'):
        shutil.copytree('/host_ssh', ssh_directory)
        for item in os.listdir(ssh_directory):
            path = os.path.join(ssh_directory, item)
            os.chown(path, 0, 0)
            os.chmod(path, 0o600)

    parts = args.remote.rsplit(':', 1)
    port = parts[1] if len(parts) > 1 else '5010'

    local_port = launcher.find_open_port('127.0.0.1', range(5010, 5110))

    cmd = [
        'ssh', '-fN', '-4',
        '-L', '{}:localhost:{}'.format(local_port, port)
     ]
    if args.ssh_key:
        cmd += ['-i', '/root/.ssh/{}'.format(args.ssh_key)]
    cmd.append(parts[0])

    print('[TUNNELING]: To remote port {}'.format(port))

    os.system(' '.join(cmd))
    return ':{}'.format(local_port)


def parse() -> argparse.Namespace:
    """
    Parse arguments from the command line.
    """
    with open('/launch/ui-description.txt') as f:
        description = f.read()

    parser = argparse.ArgumentParser(
        prog='cauldron-ui',
        description=description,
    )
    parser.add_argument('--remote', help=textwrap.dedent(
        """
        Specifies the remote SSH tunnel to create inside the UI container
        for remote kernel access. The format should be user@host-name:port.
        If port is not specified the default Cauldron kernel port of 5010
        will be used instead.
        """
    ))
    parser.add_argument('--ssh-key', help=textwrap.dedent(
        """
        Specifies the name of the SSH key to use in authenticating the
        creation of an SSH tunnel for remote kernel execution. This
        parameter is only used in combination with the --remote parameter
        and will be ignored if --remote is not set. The necessary SSH key
        should be mounted into the container's /host_ssh directory and this
        parameter should specify the name of the key within that directory.
        """
    ))
    parser.add_argument('--debug', action='store_true', help=textwrap.dedent(
        """
        Executes the Cauldron UI in debug mode for development use. Should
        not be used otherwise.
        """
    ))
    parser.add_argument(
        '--port',
        type=int,
        default=8899,
        help=textwrap.dedent(
            """
            Specifies the port that the UI should be made available on.
            """
        )
    )
    parser.add_argument(
        '-c', '--connect', '--connection',
        dest='connection_url',
        help=textwrap.dedent(
            """
            When using host networking in the container, this argument
            can be used to specify the remote kernel connection in the
            same fashion as a local cauldron ui invocation. Note that
            host networking is only available on linux systems. For
            more information see: https://docs.docker.com/network/host/
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
        'CAULDRON_REMOTE_CONNECTION': _open_remote_connection(args),
        'CAULDRON_INITIAL_DIRECTORY': '/notebooks',
        'CAULDRON_SERVER_PORT': str(gunicorn_port),
        'CAULDRON_LISTEN_PORT': str(args.port),
    }

    with open('/launch/ui-nginx.rendered.conf', 'w') as f:
        f.write(templating.render_file(
            '/launch/ui-nginx.conf',
            gunicorn_port=gunicorn_port,
            listen_port=args.port,
            debug=args.debug,
        ))
    os.system('nginx -c /launch/ui-nginx.rendered.conf')

    print('[INFO]: Internal proxy port {}'.format(gunicorn_port))
    print('[INFO]: UI listening on port {}'.format(args.port))

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
        'ui'
    ]))

    print('\n[STARTED]: Cauldron UI at http://localhost:{}'.format(args.port))
    os.system('; '.join(commands))


if __name__ == '__main__':
    main()
