import textwrap

from cauldron.environ import Response


def pretty_print_data(key, value, level: int = 0) -> list:
    whitespace = '  ' * (level + 1)
    prefix = '{}* {}:'.format(whitespace, key)
    out = [prefix]

    if level < 5 and isinstance(value, dict):
        out += [
            entry
            for k, v in value.items()
            for entry in pretty_print_data(k, v, level + 1)
        ]
    elif level < 5 and isinstance(value, (list, tuple)):
        out += [
            entry
            for i, v in enumerate(value)
            for entry in pretty_print_data(i, v, level + 1)
        ]
    else:
        out[0] = '{} {}'.format(out[0], value)

    return out


class Message(object):
    """
    Represents a failed unit test message that contains a Cauldron Response
    that should be included with the failure output
    """

    def __init__(
            self,
            name: str,
            *args: str,
            response: Response = None,
            **kwargs
    ):
        self.name = name
        self.text = ' '.join([textwrap.dedent('{}'.format(a)) for a in args])
        self.response = response
        self.data = kwargs

    def echo(self) -> str:
        out = [
            '[FAILED]: {}'.format(self.name),
            '{}'.format(self.text.strip() if self.text else '')
        ]

        out += pretty_print_data('DATA', self.data)
        out.append(self.response.echo() if self.response else '')

        return '\n'.join([entry for entry in out if entry]).strip()

    def __str__(self):
        return self.echo()
