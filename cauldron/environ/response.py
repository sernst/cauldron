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
        self.ended = False
        self.failed = False
        self.thread = None

    @property
    def response(self):
        return self.parent.response if self.parent else self

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

        for k, v in self.data.items():
            out.append('  * {}: {}'.format(k, v))

        for m in self.messages:
            out.append('--- Message [{kind}: {code}] ---\n{message}'.format(
                kind=m.kind,
                code=m.code,
                message=m.message
            ))
            for k, v in m.data.items():
                out.append('  * {}: {}'.format(k, v))

        return '\n'.join(out)

    def consume(self, other: 'Response'):
        """

        :param other:
        :return:
        """

        if self.parent:
            return self.parent.consume(other)

        def either(a, b):
            return a if a else b

        self.identifier = either(self.identifier, other.identifier)
        self.failed = self.failed or other.failed
        self.ended = self.ended or other.ended
        self.data.update(other.data)
        self.messages += other.messages
        self.thread = either(self.thread, other.thread)

        other.parent = self

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

        rm = ResponseMessage(
            kind=kind if kind else 'INFO',
            message=message,
            code=code,
            response=self
        )
        self.messages.append(rm)
        return rm

    def serialize(self) -> dict:
        """

        :return:
        """

        return dict(
            data=self.data,
            messages=[x.serialize() for x in self.messages],
            ended=self.ended,
            success=not self.failed
        )

    def fail(self, **kwargs) -> 'Response':
        """

        :param kwargs:
        :return:
        """

        self.failed = True

        if self.parent:
            return self.parent.fail(**kwargs)

        if kwargs:
            self.update(**kwargs)
        return self

    def end(self) -> 'Response':
        """

        :return:
        """

        if self.parent:
            return self.parent.end()

        self.ended = True
        return self
