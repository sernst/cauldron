import typing
import io
from pyquery import PyQuery as pq

from matplotlib import pyplot as mpl_pyplot
from matplotlib.pyplot import Figure

from bokeh import embed
from bokeh.model import Model


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


def bokeh_plot(model: Model) -> str:
    """

    :param model:
    :return:
    """

    return embed.notebook_div(model)
