import json
import os

from cauldron import cli
from cauldron import environ
from cauldron.cli import sync
from cauldron.environ.response import Response
from cauldron.cli.commands.open import opener as local_opener


def sync_open(
        context: cli.CommandContext,
        path: str
) -> Response:
    """ """

    source_directory = environ.paths.clean(path)
    source_path = os.path.join(source_directory, 'cauldron.json')

    with open(source_path, 'r') as f:
        definition = json.load(f)

    response = sync.comm.send_request(
        endpoint='/sync-open',
        remote_connection=context.remote_connection,
        data=dict(
            definition=definition,
            source_directory=source_directory,
        )
    )
    response.log_notifications()

    local_opener.update_recent_paths(response, source_directory)

    return response
