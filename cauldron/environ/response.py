import functools
import typing

from cauldron import cli
from cauldron.environ import logger


class ResponseMessage(object):

    def __init__(
            self,
            kind: str = None,
            code: str = None,
            message: str = None,
            response: 'Response' = None,
            **kwargs
    ):
        self.kind = kind
        self.code = code
        self.message = message
        self.data = kwargs
        self.response = response

    def serialize(self) -> dict:
        """

        :return:
        """
        return dict(
            kind=self.kind,
            code=self.code,
            message=self.message,
            data=self.data
        )

    def kernel(self, **kwargs) -> 'ResponseMessage':
        """

        :param kwargs:
        :return:
        """

        self.data.update(kwargs)
        return self

    def console_header(
            self,
            text: str,
            level: int = 1,
            whitespace: int = 0,
            whitespace_top: int = 1,
            whitespace_bottom: int = 0,
            trace: bool = True,
            file_path: str = None,
            append_to_file: bool = True,
            indent_by: int = 0
    ) -> 'ResponseMessage':

        logger.header(
            text=text,
            whitespace=whitespace,
            whitespace_top=whitespace_top,
            whitespace_bottom=whitespace_bottom,
            indent_by=indent_by,
            trace=trace,
            file_path=file_path,
            append_to_file=append_to_file
        )
        return self

    def console_raw(
            self,
            message: str,
            trace: bool = True,
            file_path: str = None,
            append_to_file: bool = True
    ):
        """

        :param message:
        :param trace:
        :param file_path:
        :param append_to_file:
        :return:
        """

        logger.raw(
            message=message,
            trace=trace,
            file_path=file_path,
            append_to_file=append_to_file
        )
        return self

    def console(
            self,
            message: typing.Union[str, typing.List[str]] = None,
            whitespace: int = 0,
            whitespace_top: int = 0,
            whitespace_bottom: int = 0,
            indent_by: int = 0,
            trace: bool = True,
            file_path: str = None,
            append_to_file: bool = True,
            **kwargs
    ) -> 'ResponseMessage':
        """

        :param message:
        :param whitespace:
        :param whitespace_top:
        :param whitespace_bottom:
        :param indent_by:
        :param trace:
        :param file_path:
        :param append_to_file:
        :param kwargs:
        :return:
        """

        if not message and self.message:
            message = '[{}]: {}'.format(
                self.kind,
                cli.reformat(self.message)
            )

        logger.log(
            message=message,
            whitespace=whitespace,
            whitespace_top=whitespace_top,
            whitespace_bottom=whitespace_bottom,
            indent_by=indent_by,
            trace=trace,
            file_path=file_path,
            append_to_file=append_to_file,
            **kwargs
        )
        return self

    def get_response(self) -> 'Response':
        """

        :return:
        """

        return self.response


class Response(object):
    """

    """

    def __init__(self, identifier: str = None):
        """

        """

        self.identifier = identifier
        self.data = dict()
        self.parent = None  # type: Response
        self.messages = []  # type: typing.List[ResponseMessage]
        self.errors = []  # type: typing.List[ResponseMessage]
        self.warnings = []  # type: typing.List[ResponseMessage]
        self.ended = False
        self.failed = False
        self.thread = None
        self.returned = None

    @property
    def response(self):
        return self.parent.response if self.parent else self

    def debug_echo(self) -> 'Response':
        print(self.echo())
        return self

    def echo(self) -> str:
        """

        :return:
        """
        if self.parent:
            return self.parent.echo()

        out = [
            '=== [{}] {}Response ==='.format(
                'FAILED' if self.failed else 'SUCCESS',
                '{} '.format(self.identifier) if self.identifier else ''
            )
        ]

        def print_data(key, value, level=0):
            if level < 5 and isinstance(value, dict):
                for k, v in value.items():
                    print_data(k, v, level + 1)
                return

            if level < 5 and isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    print_data(i, v, level + 1)
                return

            prefix = '  ' * (level + 1)
            value_str = '\n'.join('{}'.format(value).split('\n')[:10])[:200]
            out.append('{}* {}: {}'.format(prefix, key, value_str))

        print_data('DATA', self.data)

        for e in self.errors:
            out.append('--- ERROR [{code}] ---\n{message}'.format(
                code=e.code,
                message=e.message
            ))
            print_data('ERROR DATA', e.data)

        for w in self.warnings:
            out.append('--- WARNING [{code}] ---\n{message}'.format(
                code=w.code,
                message=w.message
            ))
            print_data('WARNING DATA', w.data)

        for m in self.messages:
            out.append('--- Message [{kind}: {code}] ---\n{message}'.format(
                kind=m.kind,
                code=m.code,
                message=m.message
            ))
            print_data('MESSAGE DATA', m.data)

        return '\n'.join(out)

    def pipe(self, function, *args, **kwargs):
        """

        :param function:
        :param args:
        :param kwargs:
        :return:
        """

        return function(self, *args, **kwargs)

    def chain(self, function, *args, **kwargs):
        """

        :param function:
        :param args:
        :param kwargs:
        :return:
        """

        return functools.partial(
            self.chain,
            self.pipe(function, *args, **kwargs)
        )

    def consume(self, other: typing.Union['Response', 'ResponseMessage']):
        """

        :param other:
        :return:
        """

        if self.parent:
            return self.parent.consume(other)

        if not other:
            # Do nothing if there is no other
            return self

        source = other.response if isinstance(other, ResponseMessage) else other

        def either(a, b):
            return a if a else b

        self.identifier = either(self.identifier, source.identifier)
        self.failed = self.failed or source.failed
        self.ended = self.ended or source.ended
        self.data.update(source.data)
        self.messages += source.messages
        self.errors += source.errors
        self.warnings += source.warnings
        self.thread = either(self.thread, source.thread)

        source.parent = self

        return self

    def update(self, **kwargs) -> 'Response':
        """

        :param kwargs:
        :return:
        """

        if self.parent:
            return self.parent.update(**kwargs)

        self.data.update(kwargs)
        return self

    def notify(
            self,
            kind: str = None,
            message: str = None,
            code: str = None,
            **kwargs
    ) -> ResponseMessage:
        """

        :return:
        """

        if self.parent:
            return self.parent.notify(kind, message, code, **kwargs)

        message_kind = (kind if kind else 'INFO').upper()
        rm = ResponseMessage(
            kind=message_kind,
            message=message,
            code=code,
            response=self,
            **kwargs
        )

        if kind == 'ERROR':
            self.errors.append(rm)
        elif kind == 'WARNING':
            self.warnings.append(rm)
        else:
            self.messages.append(rm)
        return rm

    def serialize(self) -> dict:
        """

        :return:
        """

        return dict(
            data=self.data,
            errors=[x.serialize() for x in self.errors],
            warnings=[x.serialize() for x in self.warnings],
            messages=[x.serialize() for x in self.messages],
            ended=self.ended,
            success=not self.failed
        )

    def fail(
            self,
            message: str = None,
            code: str = None,
            error: Exception = None,
            **kwargs
    ) -> ResponseMessage:
        """

        :return:
        """

        self.failed = True

        stack = logger.get_error_stack() if error else None
        error = str(error) if error else None

        return self.notify(
            kind='ERROR',
            message=cli.as_single_line(message),
            code=code,
            failed=True,
            stack=stack,
            error=error,
            **kwargs
        )

    def warn(
            self,
            message: str = None,
            code: str = None,
            **kwargs
    ) -> ResponseMessage:
        """

        :param message:
        :param code:
        :param kwargs:
        :return:
        """

        return self.notify(
            kind='WARNING',
            message=message,
            code=code,
            **kwargs
        )

    def end(self) -> 'Response':
        """

        :return:
        """

        if self.parent:
            return self.parent.end()

        self.ended = True
        return self
