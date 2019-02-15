import json as _json_io
import textwrap
import typing
from datetime import timedelta
import os as _os

import cauldron as _cd
from cauldron import environ
from cauldron import render
from cauldron.render import plots as render_plots
from cauldron.render import texts as render_texts
from cauldron.session import report


def _get_report() -> 'report.Report':
    """Fetches the report associated with the currently running step."""
    return _cd.project.get_internal_project().current_step.report


def inspect(source: dict):
    """
    Inspects the data and structure of the source dictionary object and
    adds the results to the display for viewing.

    :param source:
        A dictionary object to be inspected.
    :return:
    """
    r = _get_report()
    r.append_body(render.inspect(source))


def header(header_text: str, level: int = 1, expand_full: bool = False):
    """
    Adds a text header to the display with the specified level.

    :param header_text:
        The text to display in the header.
    :param level:
        The level of the header, which corresponds to the html header
        levels, such as <h1>, <h2>, ...
    :param expand_full:
        Whether or not the header will expand to fill the width of the entire
        notebook page, or be constrained by automatic maximum page width. The
        default value of False lines the header up with text displays.
    """
    r = _get_report()
    r.append_body(render.header(
        header_text,
        level=level,
        expand_full=expand_full
    ))


def text(value: str, preformatted: bool = False):
    """
    Adds text to the display. If the text is not preformatted, it will be
    displayed in paragraph format. Preformatted text will be displayed
    inside a pre tag with a monospace font.

    :param value:
        The text to display.
    :param preformatted:
        Whether or not to preserve the whitespace display of the text.
    """
    if preformatted:
        result = render_texts.preformatted_text(value)
    else:
        result = render_texts.text(value)
    r = _get_report()
    r.append_body(result)
    r.stdout_interceptor.write_source(
        '{}\n'.format(textwrap.dedent(value))
    )


def markdown(
        source: str = None,
        source_path: str = None,
        preserve_lines: bool = False,
        font_size: float = None,
        **kwargs
):
    """
    Renders the specified source string or source file using markdown and 
    adds the resulting HTML to the notebook display.

    :param source:
        A markdown formatted string.
    :param source_path:
        A file containing markdown text.
    :param preserve_lines:
        If True, all line breaks will be treated as hard breaks. Use this
        for pre-formatted markdown text where newlines should be retained
        during rendering.
    :param font_size:
        Specifies a relative font size adjustment. The default value is 1.0,
        which preserves the inherited font size values. Set it to a value
        below 1.0 for smaller font-size rendering and greater than 1.0 for
        larger font size rendering.
    :param kwargs:
        Any variable replacements to make within the string using Jinja2
        templating syntax.
    """
    r = _get_report()

    result = render_texts.markdown(
        source=source,
        source_path=source_path,
        preserve_lines=preserve_lines,
        font_size=font_size,
        **kwargs
    )
    r.library_includes += result['library_includes']

    r.append_body(result['body'])
    r.stdout_interceptor.write_source(
        '{}\n'.format(textwrap.dedent(result['rendered']))
    )


def json(**kwargs):
    """
    Adds the specified data to the the output display window with the
    specified key. This allows the user to make available arbitrary
    JSON-compatible data to the display for runtime use.

    :param kwargs:
        Each keyword argument is added to the CD.data object with the
        specified key and value.
    """
    r = _get_report()
    r.append_body(render.json(**kwargs))
    r.stdout_interceptor.write_source(
        '{}\n'.format(_json_io.dumps(kwargs, indent=2))
    )


def plotly(
        data: typing.Union[dict, list] = None,
        layout: dict = None,
        scale: float = 0.5,
        figure: dict = None,
        static: bool = False
):
    """
    Creates a Plotly plot in the display with the specified data and
    layout.

    :param data:
        The Plotly trace data to be plotted.
    :param layout:
        The layout data used for the plot.
    :param scale:
        The display scale with units of fractional screen height. A value
        of 0.5 constrains the output to a maximum height equal to half the
        height of browser window when viewed. Values below 1.0 are usually
        recommended so the entire output can be viewed without scrolling.
    :param figure:
        In cases where you need to create a figure instead of separate data
        and layout information, you can pass the figure here and leave the
        data and layout values as None.
    :param static:
        If true, the plot will be created without interactivity.
        This is useful if you have a lot of plots in your notebook.
    """
    r = _get_report()

    if not figure and not isinstance(data, (list, tuple)):
        data = [data]

    if 'plotly' not in r.library_includes:
        r.library_includes.append('plotly')

    r.append_body(render.plotly(
        data=data,
        layout=layout,
        scale=scale,
        figure=figure,
        static=static
    ))
    r.stdout_interceptor.write_source('[ADDED] Plotly plot\n')


def table(
        data_frame,
        scale: float = 0.7,
        include_index: bool = False,
        max_rows: int = 500
):
    """
    Adds the specified data frame to the display in a nicely formatted
    scrolling table.

    :param data_frame:
        The pandas data frame to be rendered to a table.
    :param scale:
        The display scale with units of fractional screen height. A value
        of 0.5 constrains the output to a maximum height equal to half the
        height of browser window when viewed. Values below 1.0 are usually
        recommended so the entire output can be viewed without scrolling.
    :param include_index:
        Whether or not the index column should be included in the displayed
        output. The index column is not included by default because it is
        often unnecessary extra information in the display of the data.
    :param max_rows:
        This argument exists to prevent accidentally writing very large data
        frames to a table, which can cause the notebook display to become
        sluggish or unresponsive. If you want to display large tables, you need
        only increase the value of this argument.
    """
    r = _get_report()
    r.append_body(render.table(
        data_frame=data_frame,
        scale=scale,
        include_index=include_index,
        max_rows=max_rows
    ))
    r.stdout_interceptor.write_source('[ADDED] Table\n')


def svg(svg_dom: str, filename: str = None):
    """
    Adds the specified SVG string to the display. If a filename is
    included, the SVG data will also be saved to that filename within the
    project results folder.

    :param svg_dom:
        The SVG string data to add to the display.
    :param filename:
        An optional filename where the SVG data should be saved within
        the project results folder.
    """
    r = _get_report()
    r.append_body(render.svg(svg_dom))
    r.stdout_interceptor.write_source('[ADDED] SVG\n')

    if not filename:
        return

    if not filename.endswith('.svg'):
        filename += '.svg'

    r.files[filename] = svg_dom


def jinja(path: str, **kwargs):
    """
    Renders the specified Jinja2 template to HTML and adds the output to the
    display.

    :param path:
        The fully-qualified path to the template to be rendered.
    :param kwargs:
        Any keyword arguments that will be use as variable replacements within
        the template.
    """
    r = _get_report()
    r.append_body(render.jinja(path, **kwargs))
    r.stdout_interceptor.write_source('[ADDED] Jinja2 rendered HTML\n')


def whitespace(lines: float = 1.0):
    """
    Adds the specified number of lines of whitespace.

    :param lines:
        The number of lines of whitespace to show.
    """
    r = _get_report()
    r.append_body(render.whitespace(lines))
    r.stdout_interceptor.write_source('\n')


def image(
        filename: str,
        width: int = None,
        height: int = None,
        justify: str = 'left'
):
    """
    Adds an image to the display. The image must be located within the
    assets directory of the Cauldron notebook's folder.

    :param filename:
        Name of the file within the assets directory,
    :param width:
        Optional width in pixels for the image.
    :param height:
        Optional height in pixels for the image.
    :param justify:
        One of 'left', 'center' or 'right', which specifies how the image
        is horizontally justified within the notebook display.
    """
    r = _get_report()
    path = '/'.join(['reports', r.project.uuid, 'latest', 'assets', filename])
    r.append_body(render.image(path, width, height, justify))
    r.stdout_interceptor.write_source('[ADDED] Image\n')


def html(dom: str):
    """
    A string containing a valid HTML snippet.

    :param dom:
        The HTML string to add to the display.
    """
    r = _get_report()
    r.append_body(render.html(dom))
    r.stdout_interceptor.write_source('[ADDED] HTML\n')


def workspace(show_values: bool = True, show_types: bool = True):
    """
    Adds a list of the shared variables currently stored in the project
    workspace.

    :param show_values:
        When true the values for each variable will be shown in addition to
        their name.
    :param show_types:
        When true the data types for each shared variable will be shown in
        addition to their name.
    """
    r = _get_report()

    data = {}
    for key, value in r.project.shared.fetch(None).items():
        if key.startswith('__cauldron_'):
            continue
        data[key] = value

    r.append_body(render.status(data, values=show_values, types=show_types))


def pyplot(
        figure=None,
        scale: float = 0.8,
        clear: bool = True,
        aspect_ratio: typing.Union[list, tuple] = None
):
    """
    Creates a matplotlib plot in the display for the specified figure. The size
    of the plot is determined automatically to best fit the notebook.

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
    """
    r = _get_report()
    r.append_body(render_plots.pyplot(
        figure,
        scale=scale,
        clear=clear,
        aspect_ratio=aspect_ratio
    ))
    r.stdout_interceptor.write_source('[ADDED] PyPlot plot\n')


def bokeh(model, scale: float = 0.7, responsive: bool = True):
    """
    Adds a Bokeh plot object to the notebook display.

    :param model:
        The plot object to be added to the notebook display.
    :param scale:
        How tall the plot should be in the notebook as a fraction of screen
        height. A number between 0.1 and 1.0. The default value is 0.7.
    :param responsive:
        Whether or not the plot should responsively scale to fill the width
        of the notebook. The default is True.
    """
    r = _get_report()

    if 'bokeh' not in r.library_includes:
        r.library_includes.append('bokeh')

    r.append_body(render_plots.bokeh_plot(
        model=model,
        scale=scale,
        responsive=responsive
    ))
    r.stdout_interceptor.write_source('[ADDED] Bokeh plot\n')


def listing(
        source: list,
        ordered: bool = False,
        expand_full: bool = False
):
    """
    An unordered or ordered list of the specified *source* iterable where
    each element is converted to a string representation for display.

    :param source:
        The iterable to display as a list.
    :param ordered:
        Whether or not the list should be ordered. If False, which is the
        default, an unordered bulleted list is created.
    :param expand_full:
        Whether or not the list should expand to fill the screen horizontally.
        When defaulted to False, the list is constrained to the center view
        area of the screen along with other text. This can be useful to keep
        lists aligned with the text flow.
    """
    r = _get_report()
    r.append_body(render.listing(
        source=source,
        ordered=ordered,
        expand_full=expand_full
    ))
    r.stdout_interceptor.write_source('[ADDED] Listing\n')


def list_grid(
        source: list,
        expand_full: bool = False,
        column_count: int = 2,
        row_spacing: float = 1.0
):
    """
    An multi-column list of the specified *source* iterable where
    each element is converted to a string representation for display.

    :param source:
        The iterable to display as a list.
    :param expand_full:
        Whether or not the list should expand to fill the screen horizontally.
        When defaulted to False, the list is constrained to the center view
        area of the screen along with other text. This can be useful to keep
        lists aligned with the text flow.
    :param column_count:
        The number of columns to display. The specified count is applicable to
        high-definition screens. For Lower definition screens the actual count
        displayed may be fewer as the layout responds to less available
        horizontal screen space.
    :param row_spacing:
        The number of lines of whitespace to include between each row in the
        grid. Set this to 0 for tightly displayed lists.
    """
    r = _get_report()
    r.append_body(render.list_grid(
        source=source,
        expand_full=expand_full,
        column_count=column_count,
        row_spacing=row_spacing
    ))
    r.stdout_interceptor.write_source('[ADDED] List grid\n')


def latex(source: str):
    """
    Add a mathematical equation in latex math-mode syntax to the display.
    Instead of the traditional backslash escape character, the @ character is
    used instead to prevent backslash conflicts with Python strings. For
    example, \\delta would be @delta.

    :param source:
        The string representing the latex equation to be rendered.
    """
    r = _get_report()
    if 'katex' not in r.library_includes:
        r.library_includes.append('katex')

    r.append_body(render_texts.latex(source.replace('@', '\\')))
    r.stdout_interceptor.write_source('[ADDED] Latex equation\n')


def head(source, count: int = 5):
    """
    Displays a specified number of elements in a source object of many
    different possible types.

    :param source:
        DataFrames will show *count* rows of that DataFrame. A list, tuple or
        other iterable, will show the first *count* rows. Dictionaries will
        show *count* keys from the dictionary, which will be randomly selected
        unless you are using an OrderedDict. Strings will show the first
        *count* characters.
    :param count:
        The number of elements to show from the source.
    """
    r = _get_report()
    r.append_body(render_texts.head(source, count=count))
    r.stdout_interceptor.write_source('[ADDED] Head\n')


def tail(source, count: int = 5):
    """
    The opposite of the head function. Displays the last *count* elements of
    the *source* object.

    :param source:
        DataFrames will show the last *count* rows of that DataFrame. A list,
        tuple or other iterable, will show the last *count* rows. Dictionaries
        will show *count* keys from the dictionary, which will be randomly
        selected unless you are using an OrderedDict. Strings will show the
        last *count* characters.
    :param count:
        The number of elements to show from the source.
    """
    r = _get_report()
    r.append_body(render_texts.tail(source, count=count))
    r.stdout_interceptor.write_source('[ADDED] Tail\n')


def status(
        message: str = None,
        progress: float = None,
        section_message: str = None,
        section_progress: float = None,
):
    """
    Updates the status display, which is only visible while a step is running.
    This is useful for providing feedback and information during long-running
    steps.

    A section progress is also available for cases where long running tasks
    consist of multiple tasks and you want to display sub-progress messages
    within the context of the larger status.

    Note: this is only supported when running in the Cauldron desktop
    application.

    :param message:
        The status message you want to display. If left blank the previously
        set status message will be retained. Should you desire to remove an
        existing message, specify a blank string for this argument.
    :param progress:
        A number between zero and one that indicates the overall progress for
        the current status. If no value is specified, the previously assigned
        progress will be retained.
    :param section_message:
        The status message you want to display for a particular task within a
        long-running step. If left blank the previously set section message
        will be retained. Should you desire to remove an existing message,
        specify a blank string for this argument.
    :param section_progress:
        A number between zero and one that indicates the progress for the
        current section status. If no value is specified, the previously
        assigned section progress value will be retained.
    """
    environ.abort_thread()
    step = _cd.project.get_internal_project().current_step

    if message is not None:
        step.progress_message = message
    if progress is not None:
        step.progress = max(0.0, min(1.0, progress))
    if section_message is not None:
        step.sub_progress_message = section_message
    if section_progress is not None:
        step.sub_progress = section_progress


def code_block(
        code: str = None,
        path: str = None,
        language_id: str = None,
        title: str = None,
        caption: str = None
):
    """
    Adds a block of syntax highlighted code to the display from either
    the supplied code argument, or from the code file specified
    by the path argument.

    :param code:
        A string containing the code to be added to the display
    :param path:
        A path to a file containing code to be added to the display
    :param language_id:
        The language identifier that indicates what language should
        be used by the syntax highlighter. Valid values are any of the
        languages supported by the Pygments highlighter.
    :param title:
        If specified, the code block will include a title bar with the
        value of this argument
    :param caption:
        If specified, the code block will include a caption box below the code
        that contains the value of this argument
    """
    environ.abort_thread()
    r = _get_report()
    r.append_body(render.code_block(
        block=code,
        path=path,
        language=language_id,
        title=title,
        caption=caption
    ))
    r.stdout_interceptor.write_source('{}\n'.format(code))


def elapsed():
    """
    Displays the elapsed time since the step started running.
    """
    environ.abort_thread()
    step = _cd.project.get_internal_project().current_step
    r = _get_report()
    r.append_body(render.elapsed_time(step.elapsed_time))

    result = '[ELAPSED]: {}\n'.format(timedelta(seconds=step.elapsed_time))
    r.stdout_interceptor.write_source(result)
