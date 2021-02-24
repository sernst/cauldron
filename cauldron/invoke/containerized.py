import subprocess
import textwrap

from cauldron import environ
from cauldron.ui import launcher


def run_ui(args: dict) -> int:
    """
    Start the Cauldron UI in a containerized fashion with Docker and
    support for remote connections when desired.
    """
    notebooks_directory = environ.paths.clean(
        args['notebooks_directory'] or '.'
    )

    remote = args['remote'] or ''
    user = remote.split('@', 1)[0] if remote else ''
    port = remote.rsplit(':', 1)[-1] if remote else ''
    host = (
        remote
        .replace('{}@'.format(user), '')
        .replace(':{}'.format(port), '')
    )

    exposed_port = (
        args['port']
        or port
        or launcher.find_open_port('127.0.0.1', range(8000, 9000))
    )

    cmd = [
        'docker', 'run', '--rm', '-it',
        '-p', '{}:8899'.format(exposed_port),
        '-v', '{}:/notebooks'.format(notebooks_directory),
    ]

    for variable in (args.get('environment_variables') or []):
        cmd += ['--env', variable]

    for variable in (args.get('volumes') or []):
        cmd += ['--volume', variable]

    print('\n\n--- LAUNCHING UI CONTAINER ---\n')
    print('[INFO]: Notebooks directory "{}"'.format(notebooks_directory))
    if remote:
        ssh_directory = environ.paths.clean(
            args['ssh_directory'] or '~/.ssh'
        )

        print('[INFO]: SSH directory "{}"'.format(ssh_directory))
        print('[INFO]: Remote host {}'.format(host))
        print('[INFO]: Remote user {}'.format(user))
        print('[INFO]: Remote tunnel port {}'.format(port))

        cmd += [
            '-v', '{}:/host_ssh'.format(ssh_directory),
            'swernst/cauldron:current-ui-standard',
            '--remote={}'.format(remote),
        ]
        if args['ssh_key']:
            cmd.append('--ssh-key={}'.format(args['ssh_key']))
    else:
        cmd.append('swernst/cauldron:{}'.format(args['image_tag']))

    display_command = textwrap.indent(
        ' '.join(cmd).replace(' -', '\n  -').replace('swer', '\n  swer'),
        '   '
    )
    print('\n[RUNNING]: UI container\n{}'.format(display_command))
    print('\n[STARTING]: UI at http://127.0.0.1:{}\n'.format(exposed_port))
    result = subprocess.run(cmd)
    return result.returncode
