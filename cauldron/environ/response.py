import datetime
import typing
import time

import flask
from cauldron import cli
from cauldron.cli import threads
from cauldron.environ import logger
from requests import Response as HttpResponse

ERROR_KIND = 'ERROR'
WARNING_KIND = 'WARNING'


class ResponseMessage:
    """..."""

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
        """..."""
        self.index = index
        self.kind = kind
        self.code = code
        self.message = message
        self.data = data or {}
        self.response = response
        self.log = log

    def serialize(self) -> dict:
        """..."""
        return dict(
            kind=self.kind,
            code=self.code,
            message=self.message,
            data=self.data,
            index=self.index,
            log=self.log
        )

    def kernel(self, **kwargs) -> 'ResponseMessage':
        """..."""
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
        """..."""
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
        """..."""
        logger.raw(
            message=message,
            trace=trace,
            file_path=file_path,
            append_to_file=append_to_file
        )

        self.log += message
        return self

    def console_if(
            self,
            display_condition: bool,
            message: typing.Union[str, typing.List[str]] = None,
            whitespace: int = 0,
            whitespace_top: int = 0,
            whitespace_bottom: int = 0,
            indent_by: int = 0,
            trace: bool = True,
            file_path: str = None,
            append_to_file: bool = True,
            **kwargs
    ):
        """
        Logs the ResponseMessage to the stdout with optional formatting
        specified by the arguments if the "display_condition" argument
        is True. Useful for stateful display.
        """
        if display_condition:
            return self.console(
                message=message,
                whitespace=whitespace,
                whitespace_top=whitespace_top,
                whitespace_bottom=whitespace_bottom,
                indent_by=indent_by,
                trace=trace,
                file_path=file_path,
                append_to_file=append_to_file,
                **kwargs,
            )

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
        Logs the ResponseMessage to the stdout with optional formatting
        specified by the arguments.
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
        """..."""
        return self.response


class Response:
    """..."""

    def __init__(self, identifier: str = None, failed=False):
        """Creates a new Response object."""
        self.identifier = identifier
        self.data = dict()
        self.parent = None  # type: typing.Optional[Response]
        self.messages = []  # type: typing.List[ResponseMessage]
        self.errors = []  # type: typing.List[ResponseMessage]
        self.warnings = []  # type: typing.List[ResponseMessage]
        self.ended = False
        self.failed = bool(failed)
        self.thread = None  # type: typing.Optional[threads.CauldronThread]
        self.returned = None
        self.http_response = None  # type: typing.Optional[HttpResponse]
        self._last_updated = time.time()

    @property
    def last_updated(self) -> float:
        """
        Last time the response object was updated as a unix epoch
        timestamp in seconds. Also includes thread completion time,
        which may be larger if a running thread ends without modifying
        the associated response object.
        """
        if self.thread and self.thread.completed_at:
            completed_at = self.thread.completed_at.timestamp()
        else:
            completed_at = 0
        return max(self._last_updated, completed_at)

    @property
    def success(self) -> bool:
        """..."""
        return not self.failed

    @property
    def response(self):
        """..."""
        return self.parent.response if self.parent else self

    def touch(self) -> 'Response':
        """Updates the last modified timestamp to the current time."""
        self._last_updated = time.time()
        return self

    def debug_echo(self) -> 'Response':
        """..."""
        print(self.echo())
        return self

    def returns(self, *args: typing.Any) -> 'Response':
        """Sets the returned data to send along with the response."""
        if len(args) == 0:
            self.returned = None
        elif len(args) == 1:
            self.returned = args[0]
        else:
            self.returned = args
        return self.touch()

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
        """..."""
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
        """..."""
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
        return self.touch()

    def update(self, **kwargs) -> 'Response':
        """..."""
        if self.parent:
            return self.parent.update(**kwargs)

        self.data.update(kwargs)
        return self.touch()

    def notify(
            self,
            kind: str = None,
            message: str = None,
            code: str = None,
            level: str = None,
            **kwargs
    ) -> ResponseMessage:
        """..."""
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

        if 'ERROR' in (kind, level):
            self.errors.append(rm)
        elif 'WARNING' in (kind, level):
            self.warnings.append(rm)
        else:
            self.messages.append(rm)

        self.touch()
        return rm

    def get_thread_log(self) -> typing.List[str]:
        """..."""
        return getattr(self.thread, 'logs', []) + []

    def serialize(self) -> dict:
        """..."""
        return dict(
            logs=self.get_thread_log(),
            id=self.identifier,
            data=self.data,
            errors=[x.serialize() for x in self.errors],
            warnings=[x.serialize() for x in self.warnings],
            messages=[x.serialize() for x in self.messages],
            ended=self.ended,
            success=self.success,
            timestamp=datetime.datetime.now().timestamp()
        )

    def flask_serialize(self):
        """Serializes the response into a flask JSON response."""
        return flask.jsonify(self.serialize())

    def fail(
            self,
            message: str = None,
            code: str = None,
            error: Exception = None,
            kind: str = 'ERROR',
            **kwargs
    ) -> ResponseMessage:
        """..."""
        self.failed = True

        stack = logger.get_error_stack() if error else None
        error = '{}'.format(error) if error else None

        return self.notify(
            kind=kind,
            message=cli.as_single_line(message),
            code=code,
            failed=True,
            stack=stack,
            error=error,
            level='ERROR',
            **kwargs
        )

    def warn(
            self,
            message: str = None,
            code: str = None,
            kind: str = 'WARNING',
            **kwargs
    ) -> ResponseMessage:
        """..."""
        return self.notify(
            kind=kind,
            message=message,
            code=code,
            level='WARNING',
            **kwargs
        )

    def end(self) -> 'Response':
        """..."""
        if self.parent:
            return self.parent.end()

        self.ended = True
        self.touch()
        return self

    def get_notification_log(self, start_index: int = 0) -> str:
        """..."""
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
        """..."""
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
        """Converts a serialized dictionary response to a Response object."""
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
