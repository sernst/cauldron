import json
import os
import pathlib
import textwrap
from argparse import ArgumentParser

import yaml

HUB_PREFIX = 'swernst/cauldron'
MY_DIRECTORY = pathlib.Path(__file__).parent.absolute()

BUILDS = [
    yaml.safe_load(path.read_text())
    for path in MY_DIRECTORY.joinpath('docker/build-configs').iterdir()
    if str(path).endswith('.yaml')
]

settings = json.loads(
    MY_DIRECTORY
    .joinpath('cauldron/settings.json')
    .read_text()
)
VERSION = settings['version']


def build(build_id: str, spec: dict, args: dict) -> dict:
    """Builds the container from the specified docker file path"""
    path = MY_DIRECTORY.joinpath(
        spec.get('dockerfile', 'docker-common.dockerfile')
    )

    version = '{}{}'.format(
        'pre-' if args.get('pre') else '',
        VERSION,
    )
    generic = 'pre' if args.get('pre') else 'latest'

    tags = [
        '{}:{}-{}'.format(HUB_PREFIX, version, build_id),
        '{}:{}-{}'.format(HUB_PREFIX, generic, build_id),
    ]
    if not args.get('pre'):
        tags.append('{}:current-{}'.format(HUB_PREFIX, build_id))
    if build_id == 'standard':
        tags.append('{}:{}'.format(HUB_PREFIX, generic))

    command = 'docker build --pull --file "{}" {} {} .'.format(
        path,
        ' '.join([
            '--build-arg {}={}'.format(key, value)
            for key, value in spec['build_args'].items()
        ]),
        ' '.join(['-t {}'.format(t) for t in tags])
    )

    print('[BUILDING]:', build_id)
    if args.get('dry_run'):
        print('[DRY-RUN]: Skipped building command')
        print(textwrap.indent(command.replace(' -', '\n   -'), '   '))
    else:
        os.environ['DOCKER_BUILDKIT'] = '1'
        os.system(command)

    return dict(
        spec=spec,
        id=build_id,
        path=path,
        command=command,
        tags=tags
    )


def publish(build_entry: dict, args: dict):
    """Publishes the specified build entry to docker hub"""
    skip_publishing = not build_entry.get('publish', True)
    for tag in build_entry['tags']:
        if args['dry_run']:
            print('[DRY-RUN]: Skipped pushing {}'.format(tag))
        elif skip_publishing:
            print('[SKIPPED]: Publishing not allowed for {}'.format(tag))
        else:
            print('[PUSHING]:', tag)
            os.system('docker push {}'.format(tag))


def parse() -> dict:
    """Parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        '-p', '--publish',
        action='store_true',
        help='Whether or not to publish images after building them.'
    )
    parser.add_argument(
        '-i', '--id',
        dest='ids',
        action='append',
        help=textwrap.dedent(
            """
            One or more build identifiers to build. If not specified
            all images will be built. This flag can be specified multiple
            times in a single command.
            """
        )
    )
    parser.add_argument(
        '--pre',
        action='store_true',
        help=textwrap.dedent(
            """
            If true images will be built with a "pre" in the version
            identifier and "current" images will be skipped. This is
            used to publish images for pre-releases to the hub prior
            to the official release.
            """
        )
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help=textwrap.dedent(
            """
            When set, the actual build process is skipped and instead
            the build command is printed showing what would have been
            executed.
            """
        )
    )
    return vars(parser.parse_args())


def run():
    """Execute the build process"""
    args = parse()

    build_results = [
        build(build_id, spec, args)
        for spec in BUILDS
        for build_id in spec['ids']
        if not args['ids'] or build_id in args['ids']
    ]

    if not args['publish']:
        return

    for entry in build_results:
        publish(entry, args)


if __name__ == '__main__':
    run()
