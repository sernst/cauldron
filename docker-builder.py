import os
import glob
import json
import re
from argparse import ArgumentParser

HUB_PREFIX = 'swernst/cauldron'

my_directory = os.path.dirname(os.path.realpath(__file__))
glob_path = os.path.join(my_directory, 'docker-*.dockerfile')

file_pattern = re.compile('docker-(?P<id>[^.]+).dockerfile')

with open(os.path.join(my_directory, 'cauldron', 'settings.json')) as f:
    settings = json.load(f)
version = settings['version']


def build(path: str) -> dict:
    """Builds the container from the specified docker file path"""

    match = file_pattern.search(os.path.basename(path))
    build_id = match.group('id')
    tags = [
        '{}:{}-{}'.format(HUB_PREFIX, version, build_id),
        '{}:latest-{}'.format(HUB_PREFIX, build_id)
    ]
    if build_id == 'standard':
        tags.append('{}:latest'.format(HUB_PREFIX))

    command= 'docker build --file "{}" {} .'.format(
        path,
        ' '.join(['-t {}'.format(t) for t in tags])
    )

    print('[BUILDING]:', build_id)
    os.system(command)

    return dict(
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

    return vars(parser.parse_args())


def run():
    """Execute the build process"""

    args = parse()
    build_results = [build(p) for p in glob.iglob(glob_path)]

    if not args['publish']:
        return

    for entry in build_results:
        publish(entry)


if __name__ == '__main__':
    run()
