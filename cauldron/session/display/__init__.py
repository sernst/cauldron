import typing

import cauldron
from cauldron.session import report
from cauldron import render
from cauldron import environ
from cauldron.render import texts as render_texts
from cauldron.render import plots as render_plots


def _get_report() -> 'report.Report':
    """

    :return:
    """

    return cauldron.project.internal_project.current_step.report


def inspect(source: dict):
    """
    Inspects the data and structure of the source dictionary object and
    adds the results to the display for viewing

    :param source:
        A dictionary object to be inspected
    :return:
    """

    r = _get_report()
    r.append_body(render.inspect(source))


def header(header_text: str, level: int = 1):
    """
    Adds a text header to the display with the specified level.

    :param header_text:
        The text to display in the header
    :param level:
        The level of the header, which corresponds to the html header
        levels, such as <h1>, <h2>, ...
    :return:
    """

    r = _get_report()
    r.append_body(render.header(header_text, level=level))


def text(text: str, preformatted: bool = False):
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
        result = render_texts.preformatted_text(text)
    else:
        result = render_texts.text(text)

    r = _get_report()
    r.append_body(result)


def markdown(source: str, **kwargs):
    """
    Renders the source string using markdown and adds the resulting html
    to the display

    :param source:
        A markdown formatted string
    :return:
    """

    r = _get_report()

    result = render_texts.markdown(source, **kwargs)
    r.library_includes += result['library_includes']

    r.append_body(result['body'])


def json(**kwargs):
    """
    Adds the specified data to the the output display window with the
    specified key. This allows the user to make available arbitrary
    JSON-compatible data to the display for runtime use.

    :param kwargs:
        Each keyword argument is added to the CD.data object with the
        specified key and value.
    :return:
    """

    r = _get_report()
    r.append_body(render.json(**kwargs))


def plotly(data, layout: dict, scale: float = 0.5):
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

    r = _get_report()

    if not isinstance(data, (list, tuple)):
        data = [data]

    if 'plotly' not in r.library_includes:
        r.library_includes.append('plotly')

    r.append_body(render.plotly(data, layout, scale))


def table(data_frame, scale: float = 0.7):
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

    r = _get_report()
    r.append_body(render.table(
        data_frame=data_frame,
        scale=scale
    ))


def svg(svg_dom: str, filename: str = None):
    """
    Adds the specified SVG string to the display. If a filename is
    included, the SVG data will also be saved to that filename within the
    project results folder.

    :param svg_dom:
        The SVG string data to add to the display
    :param filename:
        An optional filename where the SVG data should be saved within
        the project results folder.
    :return:
    """

    r = _get_report()
    r.append_body(render.svg(svg_dom))

    if not filename:
        return

    if not filename.endswith('.svg'):
        filename += '.svg'

    r.files[filename] = svg_dom


def jinja(path, **kwargs):
    """
    Renders the specified jinja template
    :param path:
    :param kwargs:
    :return:
    """

    r = _get_report()
    r.append_body(render.jinja(path, **kwargs))


def whitespace(lines: float = 1.0):
    """

    :param lines:
    :return:
    """

    r = _get_report()
    r.append_body(render.whitespace(lines))


def html(dom: str):
    """

    :param dom:
    :return:
    """

    r = _get_report()
    r.append_body(render.html(dom))


def workspace(values: bool = True, types: bool = True):
    """

    :param values:
    :param types:
    :return:
    """

    r = _get_report()

    if not r.project:
        return

    data = {}
    for key, value in r.project.shared.fetch(None).items():
        if key.startswith('__cauldron_'):
            continue
        data[key] = value

    r.append_body(render.status(data, values=values, types=types))


def pyplot(
        figure = None,
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

    r = _get_report()
    r.append_body(render_plots.pyplot(figure, scale=scale))


def bokeh(model, scale: float = 0.7, responsive: bool = True):
    """

    :param model:
    :param scale:
    :param responsive:
    :return:
    """

    r = _get_report()

    if 'bokeh' not in r.library_includes:
        r.library_includes.append('bokeh')

    r.append_body(render_plots.bokeh_plot(
        model=model,
        scale=scale,
        responsive=responsive
    ))


def listing(source: list, ordered: bool = False):
    """

    :param source:
    :param ordered:
    :return:
    """

    r = _get_report()
    r.append_body(render.listing(source, ordered))


def latex(source: str):
    """

    :param source:
    :return:
    """

    r = _get_report()
    if 'katex' not in r.library_includes:
        r.library_includes.append('katex')

    r.append_body(render_texts.latex(source.replace('@', '\\')))


def head(source, count: int = 5):
    """

    :param source:
    :param count:
    :return:
    """

    _get_report().append_body(render_texts.head(source, count=count))


def tail(source, count: int = 5):
    """

    :param source:
    :param count:
    :return:
    """

    _get_report().append_body(render_texts.tail(source, count=count))


def status(
        message: str = None,
        progress: float = None,
        section_message: str = None,
        section_progress: float = None,
):
    """

    :param message:
    :param progress:
    :param section_message:
    :param section_progress:
    """

    environ.abort_thread()
    step = cauldron.project.internal_project.current_step

    if message is not None:
        step.progress_message = message
    if progress is not None:
        step.progress = max(0, min(1.0, progress))
    if section_message is not None:
        step.sub_progress_message = section_message
    if section_progress is not None:
        step.sub_progress = section_progress
