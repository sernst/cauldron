import json
import os
import re
from argparse import ArgumentParser

HUB_PREFIX = 'swernst/cauldron'
MY_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
BUILDS = [
    {
        'ids': ['standard36'],
        'dockerfile': 'docker-standard.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.6', 'PYTHON_VERSION': '3.6.9'}
    },
    {
        'ids': ['ui-standard36'],
        'dockerfile': 'docker-standard-ui.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.6', 'PYTHON_VERSION': '3.6.9'}
    },
    {
        'ids': ['standard', 'standard37'],
        'dockerfile': 'docker-standard.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.7', 'PYTHON_VERSION': '3.7.5'}
    },
    {
        'ids': ['ui-standard', 'ui-standard37'],
        'dockerfile': 'docker-standard-ui.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.7', 'PYTHON_VERSION': '3.7.5'}
    },
    {
        'ids': ['standard38'],
        'dockerfile': 'docker-standard.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.8', 'PYTHON_VERSION': '3.8.0'}
    },
    {
        'ids': ['ui-standard38'],
        'dockerfile': 'docker-standard-ui.dockerfile',
        'build_args': {'PYTHON_RELEASE': '3.8', 'PYTHON_VERSION': '3.8.0'}
    },
    {
        'ids': ['miniconda'],
        'dockerfile': 'docker-miniconda.dockerfile',
        'build_args': {}
    },
    {
        'ids': ['ui-miniconda'],
        'dockerfile': 'docker-miniconda-ui.dockerfile',
        'build_args': {}
    },
    {
        'ids': ['conda'],
        'dockerfile': 'docker-conda.dockerfile',
        'build_args': {}
    },
    {
        'ids': ['ui-conda'],
        'dockerfile': 'docker-conda-ui.dockerfile',
        'build_args': {}
    },
]

with open(os.path.join(MY_DIRECTORY, 'cauldron', 'settings.json')) as f:
    settings = json.load(f)

VERSION = settings['version']


def update_base_image(path: str):
    """Pulls the latest version of the base image"""
    with open(path, 'r') as file_handle:
        contents = file_handle.read()

    regex = re.compile(r'from\s+(?P<source>[^\s]+)', re.IGNORECASE)
    matches = regex.findall(contents)

    if not matches:
        return None

    match = matches[0]
    os.system('docker pull {}'.format(match))
    return match


def build(build_id: str, spec: dict) -> dict:
    """Builds the container from the specified docker file path"""
    path = os.path.join(MY_DIRECTORY, spec['dockerfile'])
    update_base_image(path)

    tags = [
        '{}:{}-{}'.format(HUB_PREFIX, VERSION, build_id),
        '{}:latest-{}'.format(HUB_PREFIX, build_id),
        '{}:current-{}'.format(HUB_PREFIX, build_id)
    ]
    if build_id == 'standard':
        tags.append('{}:latest'.format(HUB_PREFIX))

    command = 'docker build --file "{}" {} {} .'.format(
        path,
        ' '.join([
            '--build-arg {}={}'.format(key, value)
            for key, value in spec['build_args'].items()
        ]),
        ' '.join(['-t {}'.format(t) for t in tags])
    )

    print('[BUILDING]:', build_id)
    os.system(command)

    return dict(
        spec=spec,
        id=build_id,
        path=path,
        command=command,
        tags=tags
    )


def publish(build_entry: dict):
    """Publishes the specified build entry to docker hub"""
    for tag in build_entry['tags']:
        print('[PUSHING]:', tag)
        os.system('docker push {}'.format(tag))


def parse() -> dict:
    """Parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument('-p', '--publish', action='store_true', default=False)
    parser.add_argument('-i', '--id', dest='ids', action='append')
    return vars(parser.parse_args())


def run():
    """Execute the build process"""
    args = parse()

    build_results = [
        build(build_id, spec)
        for spec in BUILDS
        for build_id in spec['ids']
        if not args['ids'] or build_id in args['ids']
    ]

    if not args['publish']:
        return

    for entry in build_results:
        publish(entry)


if __name__ == '__main__':
    run()
