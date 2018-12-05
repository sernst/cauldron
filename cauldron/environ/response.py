import typing

import flask
from requests import Response as HttpResponse

from cauldron import cli
from cauldron.cli import threads
from cauldron.environ import logger

ERROR_KIND = 'ERROR'
WARNING_KIND = 'WARNING'


class ResponseMessage(object):

    def __init__(
            self,
            kind: str = None,
            code: str = None,
            message: str = None,
            response: 'Response' = None,
            index: int = 0,
            log: str = '',
            data: dict = None
    ):
        self.index = index
        self.kind = kind
        self.code = code
        self.message = message
        self.data = data if data else {}
        self.response = response
        self.log = log

    def serialize(self) -> dict:
        """

        :return:
        """
        return dict(
            kind=self.kind,
            code=self.code,
            message=self.message,
            data=self.data,
            index=self.index,
            log=self.log
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

        self.log += logger.header(
            text=text,
            level=level,
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
    ) -> 'ResponseMessage':
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

        self.log += message
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

        self.log += logger.log(
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
    """ """

    def __init__(self, identifier: str = None, failed=False):
        """ """

        self.identifier = identifier
        self.data = dict()
        self.parent = None  # type: Response
        self.messages = []  # type: typing.List[ResponseMessage]
        self.errors = []  # type: typing.List[ResponseMessage]
        self.warnings = []  # type: typing.List[ResponseMessage]
        self.ended = False
        self.failed = bool(failed)
        self.thread = None  # type: threads.CauldronThread
        self.returned = None
        self.http_response = None  # type: HttpResponse

    @property
    def success(self) -> bool:
        return not self.failed

    @property
    def response(self):
        return self.parent.response if self.parent else self

    def debug_echo(self) -> 'Response':
        print(self.echo())
        return self

    def join(self, timeout: float = None) -> bool:
        """
        Joins on the thread associated with the response if it exists, or
        just returns after a no-op if no thread exists to join.

        :param timeout:
            Maximum number of seconds to block on the join before given up
            and continuing operation. The default `None` value will wait
            forever.
        :return:
            A boolean indicating whether or not a thread existed to join
            upon.
        """
        try:
            self.thread.join(timeout)
            return True
        except AttributeError:
            return False

    def echo(self) -> str:
        """ """

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

        def print_item(kind: str, item: 'ResponseMessage'):
            print_data('{} DATA'.format(kind), item.data)
            return '--- {kind} [{code}] ---\n{message}'.format(
                code=item.code,
                message=item.message,
                kind=item.kind
            )

        notifications = dict(
            ERROR=self.errors,
            WARNING=self.warnings,
            MESSAGE=self.messages
        )

        out += [
            print_item(kind, item)
            for kind, items in notifications.items()
            for item in items
        ]

        return '\n'.join(out)

    def consume(
            self,
            other: typing.Union['Response', 'ResponseMessage']
    ) -> 'Response':
        """

        :param other:
        :return:
        """

        if other == self:
            return self

        if self.parent:
            return self.parent.consume(other)

        if not other:
            # Do nothing if there is no other
            return self

        source = other.response

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
        """ """

        if self.parent:
            return self.parent.notify(kind, message, code, **kwargs)

        message_kind = (kind or 'INFO').upper()
        index = sum([len(self.messages), len(self.errors), len(self.warnings)])
        rm = ResponseMessage(
            kind=message_kind,
            message=message,
            code=code,
            response=self,
            index=index,
            data=kwargs
        )

        if kind == 'ERROR':
            self.errors.append(rm)
        elif kind == 'WARNING':
            self.warnings.append(rm)
        else:
            self.messages.append(rm)
        return rm

    def get_thread_log(self) -> typing.List[str]:
        """ """

        return getattr(self.thread, 'logs', []) + []

    def serialize(self) -> dict:
        """ """

        return dict(
            logs=self.get_thread_log(),
            id=self.identifier,
            data=self.data,
            errors=[x.serialize() for x in self.errors],
            warnings=[x.serialize() for x in self.warnings],
            messages=[x.serialize() for x in self.messages],
            ended=self.ended,
            success=self.success
        )

    def flask_serialize(self):
        """ Serializes the response into a flask JSON response """

        return flask.jsonify(self.serialize())

    def fail(
            self,
            message: str = None,
            code: str = None,
            error: Exception = None,
            **kwargs
    ) -> ResponseMessage:
        """ """

        self.failed = True

        stack = logger.get_error_stack() if error else None
        error = '{}'.format(error) if error else None

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
        """ """

        if self.parent:
            return self.parent.end()

        self.ended = True
        return self

    def get_notification_log(self, start_index: int = 0) -> str:
        """ """

        notifications = sorted(
            self.messages + self.warnings + self.errors,
            key=lambda x: x.index
        )

        logs = [x.log for x in notifications if x.index >= start_index]
        return '\n'.join(logs)

    def log_notifications(
            self,
            start_index: int = 0,
            trace: bool = True,
            file_path: str = None,
            append_to_file: bool = True
    ) -> str:
        """ """

        message = self.get_notification_log(start_index)
        logger.raw(
            message=message,
            trace=trace,
            file_path=file_path,
            append_to_file=append_to_file
        )
        return message

    @staticmethod
    def deserialize(serial_data: dict) -> 'Response':
        """ Converts a serialized dictionary response to a Response object """

        r = Response(serial_data.get('id'))
        r.data.update(serial_data.get('data', {}))
        r.ended = serial_data.get('ended', False)
        r.failed = not serial_data.get('success', True)

        def load_messages(message_type: str):
            messages = [
                ResponseMessage(**data)
                for data in serial_data.get(message_type, [])
            ]
            setattr(r, message_type, getattr(r, message_type) + messages)

        load_messages('errors')
        load_messages('warnings')
        load_messages('messages')

        return r
