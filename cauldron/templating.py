import typing
import textwrap
import time
import random
import string

from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import contextfilter
from jinja2.runtime import Context

from cauldron import environ
from cauldron.render import utils

BASE_TIME = time.time()
JINJA_ENVIRONMENT = Environment()

@contextfilter
def get_id(context: Context, prefix: str) -> str:
    """

    :param context:
    :param prefix:
    :return:
    """

    return 'cdi-{}-{}'.format(
        prefix,
        context['cauldron_template_uid']
    )


@contextfilter
def get_latex(content:Context, prefix: str) -> str:
    """

    :param content:
    :param prefix:
    :return:
    """

    return '\n\n{}\n\n'.format(render_template(
        'katex.html',
        source=utils.format_latex(prefix)
    ))


def make_template_uid() -> str:
    """

    :return:
    """

    return '{}-{}'.format(
        format(int(1000.0 * (time.time() - BASE_TIME)), 'x'),
        ''.join(random.choice(string.ascii_lowercase) for x in range(8))
    )


def get_environment() -> Environment:
    """
    Returns the jinja2 templating environment updated with the most recent
    cauldron environment configurations

    :return:
    """

    env = JINJA_ENVIRONMENT

    loader = env.loader
    resource_path = environ.configs.make_path(
        'resources', 'templates',
        override_key='template_path'
    )

    if not loader:
        env.filters['id'] = get_id
        env.filters['latex'] = get_latex

    if not loader or resource_path not in loader.searchpath:
        env.loader = FileSystemLoader(resource_path)

    return env


def render(template: typing.Union[str, Template], **kwargs):
    """

    :param template:
    :param kwargs:
    :return:
    """

    if not hasattr(template, 'render'):
        template = get_environment().from_string(textwrap.dedent(template))

    return template.render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )


def render_file(path: str, **kwargs):
    """

    :param path:
    :param kwargs:
    :return:
    """

    with open(path, 'r+') as f:
        contents = f.read()

    return get_environment().from_string(contents).render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )


def render_template(template_name: str, **kwargs):
    """

    :param template_name:
    :param kwargs:
    :return:
    """

    return get_environment().get_template(template_name).render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )
