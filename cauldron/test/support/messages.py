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

        if self.text:
            out.append('{}'.format(self.text.strip()))

        for k, v in self.data.items():
            out.append('   * {}: {}'.format(k, v))

        if self.response:
            if not hasattr(self.response, 'echo'):
                out += [r.echo() for r in self.response]
            else:
                out.append(self.response.echo())

        return '\n'.join(out)

    def __unicode__(self):
        return self.__str__()
