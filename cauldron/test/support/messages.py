import typing
from cauldron.environ import Response


class Message(object):

    def __init__(
            self,
            name: str,
            *args: typing.List[str],
            response: typing.Union[Response, typing.List[Response]] = None,
            **kwargs
    ):
        self.name = name
        self.text = ' '.join(['{}'.format(a) for a in args])
        self.response = response
        self.data = kwargs

    def __str__(self):
        out = ['[FAILED]: {}'.format(self.name)]

        def print_data(key, value, level = 0):
            if level < 5 and isinstance(value, dict):
                for k, v in value.items():
                    print_data(k, v, level + 1)
                return

            if level < 5 and isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    print_data(i, v, level + 1)
                return

            prefix = '  ' * (level + 1)
            out.append('{}* {}: {}'.format(prefix, key, value))

        if self.text:
            out.append('{}'.format(self.text.strip()))

        print_data('DATA', self.data)

        if self.response:
            if not hasattr(self.response, 'echo'):
                out += [r.echo() for r in self.response]
            else:
                out.append(self.response.echo())

        return '\n'.join(out)

    def __unicode__(self):
        return self.__str__()
