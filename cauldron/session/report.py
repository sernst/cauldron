import io

from cauldron.render import texts as render_texts
from cauldron.session.caching import SharedCache


class Report(object):
    """
    The display management class for each step in a project. These class
    instances are exposed to Cauldron users, which provide the functionality
    for adding various element types to the display.
    """

    def __init__(self, step=None):
        self.step = step
        self.body = []
        self.css = []
        self.data = SharedCache()
        self.files = SharedCache()
        self.title = self.definition.get('title')
        self.subtitle = self.definition.get('subtitle')
        self.summary = self.definition.get('summary')
        self.library_includes = []
        self.print_buffer = None  # type: io.StringIO

    @property
    def project(self):
        return self.step.project if self.step else None

    @property
    def id(self):
        return self.step.definition.name if self.step else None

    @property
    def definition(self):
        return self.step.definition if self.step else None

    def clear(self):
        """
        Clear all user-data stored in this instance and reset it to its
        originally loaded state

        :return:
            The instance that was called for method chaining
        """
        self.body = []
        self.data = SharedCache()
        self.files = SharedCache()
        return self

    def append_body(self, dom: str):
        """

        :param dom:
        :return:
        """

        self.flush_prints()
        self.body.append(dom)

    def flush_prints(self):
        """

        :return:
        """

        if not self.print_buffer:
            return

        contents = self.print_buffer.getvalue()
        self.print_buffer.truncate(0)
        self.print_buffer.seek(0)
        self.body.append(render_texts.preformatted_text(contents))
