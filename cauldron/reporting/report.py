from cauldron import render
from cauldron.session.caching import SharedCache


class Report(object):
    """
    A class for storing the elements of the
    """

    def __init__(self, identifier: str, project=None, **kwargs):
        self.id = identifier
        self.body = []
        self.css = []
        self.data = SharedCache()
        self.files = SharedCache()
        self.project = project
        self.title = kwargs.get('title')
        self.summary = kwargs.get('summary')

    def clear(self):
        self.body = []
        self.data = SharedCache()
        self.files = SharedCache()

    def header(self, text: str, level: int = 1):
        """

        :param text:
        :param level:
        :return:
        """

        self.body.append(render.header(text, level=level))

    def text(self, text: str, preformatted: bool = False):
        """

        :param text:
        :param preformatted:
        :return:
        """

        if preformatted:
            result = render.preformatted_text(text)
        else:
            result = render.text(text)
        self.body.append(result)

    def markdown(self, source: str, **kwargs):
        """

        :param source:
        :return:
        """

        self.body.append(render.markdown(source, **kwargs))

    def json(self, window_key: str, data):
        """

        :param window_key:
        :param data:
        :return:
        """

        self.body.append(render.json(window_key, data))

    def add_html(self, content):
        """

        :param content:
        :return:
        """

        self.body.append(render.html(content))

    def plotly(self, data, layout: dict, scale: float = 0.5):
        """

        :param data:
        :param layout:
        :param scale:
        :return:
        """

        if not isinstance(data, (list, tuple)):
            data = [data]

        self.body.append(render.plotly(data, layout, scale))

    def table(self, data_frame, scale: float = 0.7):
        """

        :param data_frame:
        :param scale:
        :return:
        """

        self.body.append(render.table(
            data_frame=data_frame,
            scale=scale
        ))

    def svg(self, svg: str, filename: str = None):
        """

        :param svg:
        :param filename:
        :return:
        """

        self.body.append(render.svg(svg))

        if not filename:
            return

        if not filename.endswith('.svg'):
            filename += '.svg'

        self.files[filename] = svg

    def jinja(self, path, **kwargs):
        """

        :param path:
        :param kwargs:
        :return:
        """

        self.body.append(render.jinja(path, **kwargs))

    def whitespace(self, lines: float = 1.0):
        """

        :param lines:
        :return:
        """

        self.body.append(render.whitespace(lines))

    def html(self, dom: str):
        """

        :param dom:
        :return:
        """

        self.body.append(render.html(dom))

    def workspace(self, values: bool = True, types: bool = True):
        """

        :param values:
        :param types:
        :return:
        """

        if not self.project:
            return

        data = {}
        for key, value in self.project.shared.fetch(None).items():
            if key.startswith('__cauldron_'):
                continue
            data[key] = value

        self.body.append(render.status(data, values=values, types=types))
