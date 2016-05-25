import typing

from matplotlib.pyplot import Figure

from cauldron import render
from cauldron.render import plots as render_plots
from cauldron.session.caching import SharedCache


class Report(object):
    """
    A class for storing the elements of the
    """

    def __init__(self, project=None, definition: dict = None):
        self.definition = {} if definition is None else definition
        self.id = self.definition.get('name', 'unknown-step')
        self.body = []
        self.css = []
        self.data = SharedCache()
        self.files = SharedCache()
        self.project = project
        self.title = self.definition.get('title')
        self.subtitle = self.definition.get('subtitle')
        self.summary = self.definition.get('summary')

    def clear(self):
        self.body = []
        self.data = SharedCache()
        self.files = SharedCache()

    def inspect(self, source: dict):
        """

        :param source:
        :return:
        """

        self.body.append(render.inspect(source))

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

    def pyplot(
            self,
            figure: Figure = None,
            scale: float = 0.8,
            clear: bool = True,
            aspect_ratio: typing.Union[list, tuple] = None
    ):
        """

        :param figure:
            The matplotlib figure to plot. If omitted, the currently active
            figure will be used.
        :param scale:
            The display scale with units of fractional screen height. A value
            of 0.5 constrains the output to a maximum height equal to half the
            height of browser window when viewed. Values below 1.0 are usually
            recommended so the entire output can be viewed without scrolling.
        :param clear:
            Clears the figure after it has been rendered. This is useful to
            prevent persisting old plot data between repeated runs of the
            project files. This can be disabled if the plot is going to be
            used later in the project files.
        :param aspect_ratio:
            The aspect ratio for the displayed plot as a two-element list or
            tuple. The first element is the width and the second element the
            height. The units are "inches," which is an important consideration
            for the display of text within the figure. If no aspect ratio is
            specified, the currently assigned values to the plot will be used
            instead.
        :return:
        """

        self.body.append(render_plots.pyplot(figure, scale=scale))
