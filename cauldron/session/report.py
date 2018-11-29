import os
import time
import typing

from cauldron.render import texts as render_texts
from cauldron.session import projects
from cauldron.session.buffering import RedirectBuffer
from cauldron.session.caching import SharedCache
from cauldron.session import definitions


class Report(object):
    """
    The display management class for each step in a project. These class
    instances are exposed to Cauldron users, which provide the functionality
    for adding various element types to the display.
    """

    def __init__(self, step=None):
        self.step = step  # type: projects.ProjectStep
        self.body = []  # type: typing.List[str]
        self.css = []  # type: typing.List[str]
        self.data = SharedCache()
        self.files = SharedCache()
        self.title = (
            self.definition.title
            if hasattr(self.definition, 'title') else
            self.definition.get('title')
        )
        self.subtitle = self.definition.get('subtitle')
        self.summary = self.definition.get('summary')
        self.library_includes = []
        self.stdout_interceptor = None  # type: RedirectBuffer
        self.stderr_interceptor = None  # type: RedirectBuffer
        self._last_update_time = 0

    @property
    def last_update_time(self) -> float:
        """The last time at which the report was modified."""
        stdout = self.stdout_interceptor
        stderr = self.stderr_interceptor

        return max([
            self._last_update_time,
            stdout.last_write_time if stdout else 0,
            stderr.last_write_time if stderr else 0,
        ])

    @property
    def project(self) -> typing.Union['projects.Project', None]:
        """
        Project in which this report resides if such a project
        exists or None otherwise.
        """
        return self.step.project if self.step else None

    @property
    def results_cache_path(self) -> str:
        """
        Location where step report is cached between sessions to
        prevent loss of display data between runs.
        """
        if not self.project:
            return ''
        return os.path.join(
            self.project.results_path,
            '.cache',
            'steps',
            '{}.json'.format(self.id)
        )

    @property
    def id(self):
        return self.step.definition.name if self.step else None

    @property
    def definition(
            self
    ) -> typing.Union[None, dict, 'definitions.FileDefinition']:
        return self.step.definition if self.step else None

    def clear(self) -> 'Report':
        """
        Clear all user-data stored in this instance and reset it to its
        originally loaded state

        :return:
            The instance that was called for method chaining
        """
        self.body = []
        self.data = SharedCache()
        self.files = SharedCache()
        self._last_update_time = time.time()
        return self

    def append_body(self, dom: str):
        """
        Appends the specified HTML-formatted DOM string to the
        currently stored report body for the step.
        """
        self.flush_stdout()
        self.body.append(dom)
        self._last_update_time = time.time()

    def read_stdout(self):
        """
        Reads the current state of the print buffer (if it exists) and returns
        a body-ready dom object of those contents without adding them to the
        actual report body. This is useful for creating intermediate body
        values for display while the method is still executing.

        :return:
            A dom string for the current state of the print buffer contents
        """
        try:
            contents = self.stdout_interceptor.read_all()
        except Exception as err:
            contents = ''

        return render_texts.preformatted_text(contents)

    def flush_stdout(self):
        """
        Empties the standard out redirect buffer and renders the
        contents to the body as a preformatted text box.
        """
        try:
            contents = self.stdout_interceptor.flush_all()
        except Exception:
            return

        if len(contents) > 0:
            self.body.append(render_texts.preformatted_text(contents))
            self._last_update_time = time.time()

        return contents

    def read_stderr(self):
        """
        Returns the current state of the stderr redirect buffer This is useful
        for creating intermediate display values while the step is still
        executing.

        :return:
            A string of the current state of the stderr redirect buffer contents
        """
        try:
            return self.stderr_interceptor.read_all()
        except Exception:
            return ''

    def flush_stderr(self) -> str:
        """Empties the standard error redirect buffer."""
        try:
            return self.stderr_interceptor.flush_all()
        except Exception:
            return ''
