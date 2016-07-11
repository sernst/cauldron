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
    A jinja2 context filter for creating reusable unique identifiers within a
    cauldron display. The uid is designed to be unique within each step within
    a project, as well as unique each time that step is rendered. A UID is
    made up of three pieces::

        cdi-[PREFIX]-[RENDER_HASH]

    The "cdi" is a universal prefix that prevents any possible collision with
    non-cauldron IDs in the page. The [PREFIX] is supplied by the prefix
    argument to separate different IDs inside the same render step. The
    [RENDER_HASH] is a unique character string that is created uniquely each
    time a render step completes.

    :param context:
        Jinja2 context in which this filter is being applied
    :param prefix:
        Prefix string that indicates which uid is being created within a step
    :return:
        A uniquely identifying string
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
    Renders a template string using Jinja2 and the Cauldron templating
    environment.

    :param template:
        The string containing the template to be rendered
    :param kwargs:
        Any named arguments to pass to Jinja2 for use in rendering
    :return:
        The rendered template string
    """

    if not hasattr(template, 'render'):
        template = get_environment().from_string(textwrap.dedent(template))

    return template.render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )


def render_file(path: str, **kwargs):
    """
    Renders a file at the specified absolute path. The file can reside
    anywhere on the local disk as Cauldron's template environment path
    searching is ignored.

    :param path:
        Absolute path to a template file to render
    :param kwargs:
        Named arguments that should be passed to Jinja2 for rendering
    :return:
        The rendered template string
    """

    with open(path, 'r+') as f:
        contents = f.read()

    return get_environment().from_string(contents).render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )


def render_template(template_name: str, **kwargs):
    """
    Renders the template file with the given filename from within Cauldron's
    template environment folder.

    :param template_name:
        The filename of the template to render. Any path elements should be
        relative to Cauldron's root template folder.
    :param kwargs:
        Any elements passed to Jinja2 for rendering the template
    :return:
        The rendered string
    """

    return get_environment().get_template(template_name).render(
        cauldron_template_uid=make_template_uid(),
        **kwargs
    )
