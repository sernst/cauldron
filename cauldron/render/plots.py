import typing
import io
from pyquery import PyQuery as pq

from cauldron import templating

try:
    from matplotlib import pyplot as mpl_pyplot
    from matplotlib.pyplot import Figure
except Exception:
    mpl_pyplot = None
    Figure = None

try:
    from bokeh import embed
    from bokeh.model import Model
except Exception:
    embed = None
    Model = None


def pyplot(
        figure: Figure = None,
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

    if not figure:
        figure = mpl_pyplot.gcf()

    if aspect_ratio:
        figure.set_size_inches(
            aspect_ratio[0],
            aspect_ratio[1]
        )

    buffer = io.StringIO()
    figure.savefig(
        buffer,
        format='svg',
        dpi=300
    )
    buffer.seek(0)
    svg_dta = buffer.read()

    if clear:
        figure.clear()

    dom = pq('<div class="cd-pylab-plot">{}</div>'.format(svg_dta))
    svg = dom('svg')
    svg.add_class('cd-pylab-svg')
    svg.css('max-height', '{}vh'.format(int(100.0 * scale)))
    svg.attr('width', '100%')
    svg.attr('height', '100%')

    return dom.html()


def bokeh_plot(
        model: Model,
        scale: float = 0.7,
        responsive: bool = True
) -> str:
    """

    :param model:
    :param scale:
    :param responsive:
    :return:
    """

    if responsive:
        model.responsive = True
        model.plot_width = 800
        model.plot_height = round((scale * 9 / 16) * 800)

    results = embed.components(model, wrap_plot_info=False)

    return templating.render_template(
        'bokeh_component.html',
        script=results[0],
        id=results[1]['elementid'],
        model_id=results[1]['modelid'],
        scale=round(100 * scale) if scale is not None else 1000
    )
