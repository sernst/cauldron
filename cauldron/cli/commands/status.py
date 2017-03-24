import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron.environ import Response

NAME = 'status'
DESCRIPTION = (
    """
    Displays the status of project and the shared workspace variables
    """
)


def to_console_formatted_string(data: dict) -> str:
    """ """

    def make_line(key: str) -> str:
        if key.startswith('__cauldron_'):
            return ''

        data_class = getattr(data[key], '__class__', data[key])
        data_type = getattr(data_class, '__name__', type(data[key]))

        value = '{}'.format(data[key])[:250].replace('\n', '\n   ')
        if value.find('\n') != -1:
            value = '\n{}'.format(value)

        return '+ {name} ({type}): {value}'.format(
            name=key,
            type=data_type,
            value=value
        )

    keys = list(data.keys())
    keys.sort()
    lines = list(filter(
        lambda line: len(line) > 0,
        [make_line(key) for key in keys]
    ))

    return '\n'.join(lines)


def execute_remote(context: cli.CommandContext) -> Response:
    """ """

    thread = sync.send_remote_command(
        command=context.name,
        raw_args=context.raw_args,
        asynchronous=False
    )

    thread.join()

    response = thread.responses[0]
    response.log_notifications()
    return context.response.consume(response)


def execute(context: cli.CommandContext) -> Response:
    response = context.response
    project = cauldron.project.internal_project

    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is currently open'
        ).console(
            whitespace=1
        ).response

    try:
        output = to_console_formatted_string(project.shared.fetch(None))
    except Exception as err:
        return response.fail(
            code='STATUS_ERROR',
            message='Failed to process shared variables for display'
        ).console(
            whitespace=1
        ).response

    return response.notify(
        kind='SUCCESS',
        code='STATUS_CREATED',
        message='Status created'
    ).console(
        message=output,
        whitespace=1
    ).response
