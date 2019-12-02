import os
import sys

my_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(my_directory)


def run_build():
    """Builds the Cauldron container image"""
    os.chdir(my_directory)

    cmd = [
        'docker',
        'build',
        '-t', 'cauldron_app',
        '.'
    ]

    return os.system(' '.join(cmd))


def run_container():
    """Runs an interactive container"""

    os.chdir(my_directory)

    cmd = [
        'docker', 'run',
        '-it', '--rm',
        '-v', '{}:/cauldron'.format(my_directory),
        '-p', '5010:5010',
        'cauldron_app',
        '/bin/bash'
    ]

    return os.system(' '.join(cmd))


def run_test():
    """Runs through python tests"""

    os.chdir(my_directory)

    import pytest

    return pytest.main([
        '--cov-report',
        'term',
        '--cov=cauldron',
        '{}'.format(os.path.join(my_directory, 'cauldron', 'test'))
    ])


def run():
    """Execute the Cauldron container command"""

    command = sys.argv[1].strip().lower()
    print('[COMMAND]:', command)

    if command == 'test':
        return run_test()
    elif command == 'build':
        return run_build()
    elif command == 'up':
        return run_container()
    elif command == 'serve':
        import cauldron
        cauldron.run_server(port=5010, public=True)


if __name__ == '__main__':
    run()
