import typing
import io

from cauldron import templating
from cauldron import environ


def pyplot(
        figure=None,
        scale: float = 0.8,
        clear: bool = True,
        aspect_ratio: typing.Union[list, tuple] = None
) -> str:
    """

    :param figure:
    :param scale:
    :param clear:
    :param aspect_ratio:
    :return:
    """

    environ.abort_thread()

    from bs4 import BeautifulSoup

    try:
        from matplotlib import pyplot as mpl_pyplot
    except Exception:
        mpl_pyplot = None

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
    figure.savefig(
        buffer,
        format='svg',
        dpi=300
    )
    buffer.seek(0)
    svg_data = buffer.read()

    if clear:
        figure.clear()

    soup = BeautifulSoup(svg_data, 'html.parser')

    svg_tag = soup.find_all('svg')[0]
    svg_tag['width'] = '100%'
    svg_tag['height'] = '100%'

    classes = svg_tag.get('class', '').strip().split(' ')
    classes.append('cd-pylab-svg')
    svg_tag['class'] = '\n'.join(classes)

    styles = [
        s for s in svg_tag.get('style', '').split(';')
        if len(s.strip()) > 1
    ]
    styles.append('max-height:{}vh;'.format(int(100.0 * scale)))
    svg_tag['style'] = ';'.join(styles)

    return '<div class="cd-pylab-plot">{}</div>'.format(soup.prettify())


def bokeh_plot(
        model,
        scale: float = 0.7,
        responsive: bool = True
) -> str:
    """

    :param model:
    :param scale:
    :param responsive:
    :return:
    """

    environ.abort_thread()

    try:
        from bokeh import embed
    except Exception:
        embed = None

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
