import typing

import pandas as pd
from matplotlib.pyplot import Figure

from cauldron import render
from cauldron.render import plots as render_plots
from cauldron.session.caching import SharedCache


class Report(object):
    """
    The display management class for each step in a project. These class
    instances are exposed to Cauldron users, which provide the functionality
    for adding various element types to the display.
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
        self.library_includes = []

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

    def inspect(self, source: dict):
        """
        Inspects the data and structure of the source dictionary object and
        adds the results to the display for viewing

        :param source:
            A dictionary object to be inspected
        :return:
        """

        self.body.append(render.inspect(source))

    def header(self, text: str, level: int = 1):
        """
        Adds a text header to the display with the specified level.

        :param text:
            The text to display in the header
        :param level:
            The level of the header, which corresponds to the html header
            levels, such as <h1>, <h2>, ...
        :return:
        """

        self.body.append(render.header(text, level=level))

    def text(self, text: str, preformatted: bool = False):
        """
        Adds text to the display. If the text is not preformatted, it will be
        displayed in paragraph format. Preformatted text will be displayed
        inside a pre tag with a monospace font.

        :param text:
            The text to display
        :param preformatted:
            Whether or not to preserve the whitespace display the text
        :return:
        """

        if preformatted:
            result = render.preformatted_text(text)
        else:
            result = render.text(text)
        self.body.append(result)

    def markdown(self, source: str, **kwargs):
        """
        Renders the source string using markdown and adds the resulting html
        to the display

        :param source:
            A markdown formatted string
        :return:
        """

        self.body.append(render.markdown(source, **kwargs))

    def json(self, window_key: str, data):
        """
        Adds the specified data to the the output display window with the
        specified key. This allows the user to make available arbitrary
        JSON-compatible data to the display for runtime use.

        :param window_key:
            The key on the global window object to which this data will be
            assigned.
        :param data:
            The data to be assigned to the window object. This data must be
            serializable as JSON data.
        :return:
        """

        self.body.append(render.json(window_key, data))

    def add_html(self, dom: str):
        """
        Add the specified html string to the display

        :param content:
            A string containing html to be added to the display
        :return:
        """

        self.body.append(render.html(dom))

    def plotly(self, data, layout: dict, scale: float = 0.5):
        """
        Creates a plotly plot in the display with the specified data and layout

        :param data:
            The plotly trace data to be plotted
        :param layout:
            The layout data used for the plot
        :param scale:
            The display scale with units of fractional screen height. A value
            of 0.5 constrains the output to a maximum height equal to half the
            height of browser window when viewed. Values below 1.0 are usually
            recommended so the entire output can be viewed without scrolling.

        :return:
        """

        if not isinstance(data, (list, tuple)):
            data = [data]

        if 'plotly' not in self.library_includes:
            self.library_includes.append('plotly')

        self.body.append(render.plotly(data, layout, scale))

    def table(self, data_frame: pd.DataFrame, scale: float = 0.7):
        """
        Adds the specified data frame to the display in a nicely formatted
        scrolling table

        :param data_frame:
            The pandas data frame to be rendered to a table
        :param scale:
            The display scale with units of fractional screen height. A value
            of 0.5 constrains the output to a maximum height equal to half the
            height of browser window when viewed. Values below 1.0 are usually
            recommended so the entire output can be viewed without scrolling.
        :return:
        """

        self.body.append(render.table(
            data_frame=data_frame,
            scale=scale
        ))

    def svg(self, svg: str, filename: str = None):
        """
        Adds the specified SVG string to the display. If a filename is
        included, the SVG data will also be saved to that filename within the
        project results folder.

        :param svg:
            The SVG string data to add to the display
        :param filename:
            An optional filename where the SVG data should be saved within
            the project results folder.
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
        Renders the specified jinja template
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

    def bokeh(self, model):
        """

        :param model:
        :return:
        """

        if 'bokeh' not in self.library_includes:
            self.library_includes.append('bokeh')

        self.body.append(render_plots.bokeh_plot(model))

    def listing(self, source: list, ordered: bool = False):
        """

        :param source:
        :param ordered:
        :return:
        """

        self.body.append(render.listing(source, ordered))
