import io
import typing

from cauldron import environ
from cauldron import templating


def pyplot(
        figure=None,
        scale: float = 0.8,
        clear: bool = True,
        aspect_ratio: typing.Union[list, tuple] = None
) -> str:
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
    environ.abort_thread()

    try:
        import bs4
    except ImportError:
        return templating.render_template(
            template_name='import-error.html',
            library_name='beautifulsoup4',
            additional_info="""
                The beatifulsoup4 library is needed to manage the
                display of matplotlib graphics within the notebook
                display.
                """
        )

    try:
        from matplotlib import pyplot as mpl_pyplot
    except ImportError:
        return templating.render_template(
            template_name='import-error.html',
            library_name='matplotlib'
        )

    if not figure:
        figure = mpl_pyplot.gcf()

    if aspect_ratio:
        figure.set_size_inches(
            aspect_ratio[0],
            aspect_ratio[1]
        )
    else:
        figure.set_size_inches(12, 8)

    buffer = io.StringIO()
    figure.savefig(buffer, format='svg', dpi=300)
    buffer.seek(0)
    svg_data = buffer.read()

    if clear:
        figure.clear()

    soup = bs4.BeautifulSoup(svg_data, 'html.parser')
    uid = templating.make_template_uid()

    # Pyplot uses a * style tag, which is completely inappropriate
    # and needs to be refined to prevent styles spilling out into
    # other areas of the notebook.
    for style_tag in soup.find_all('style'):
        style_tag.string = style_tag.string.replace(
            '*{',
            '.cd-pylab-svg-{} *{{'.format(uid)
        )

    svg_tag = soup.find_all('svg')[0]
    svg_tag['width'] = '100%'
    svg_tag['height'] = '100%'

    classes = svg_tag.get('class', '').strip().split(' ')
    classes.append('cd-pylab-svg-{}'.format(uid))
    svg_tag['class'] = ' '.join(classes).strip()

    styles = [
        s for s in svg_tag.get('style', '').split(';')
        if len(s.strip()) > 1
    ]
    styles.append('max-height:{}vh;'.format(int(100.0 * scale)))
    svg_tag['style'] = ';'.join(styles).strip()

    result = '<div class="cd-pylab-plot">{}</div>'.format(soup.prettify())
    return result


def bokeh_plot(
        model,
        scale: float = 0.7,
        responsive: bool = True
) -> str:
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
    environ.abort_thread()

    try:
        from bokeh import embed
    except ImportError:
        return templating.render_template(
            template_name='import-error.html',
            library_name='bokeh'
        )

    if responsive:
        model.sizing_mode = "scale_width"
        # model.responsive = True
        model.plot_width = 800
        model.plot_height = round((scale * 9 / 16) * 800)

    results = embed.components(model)

    script = results[0] \
        .split('>', 1)[1] \
        .rsplit('</', 1)[0]

    return templating.render_template(
        'bokeh_component.html',
        script=script,
        dom=results[1],
        scale=round(100 * scale) if scale is not None else 1000
    )
