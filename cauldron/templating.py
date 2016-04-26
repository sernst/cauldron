import typing
import textwrap

from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader

from cauldron import environ


def render(template: typing.Union[str, Template], **kwargs):
    """

    :param template:
    :param kwargs:
    :return:
    """

    if not hasattr(template, 'render'):
        template = Template(textwrap.dedent(template))

    return template.render(**kwargs)


def render_file(path: str, **kwargs):
    """

    :param path:
    :param kwargs:
    :return:
    """

    with open(path, 'r+') as f:
        contents = f.read()

    return Template(contents).render(**kwargs)


def render_template(name: str, **kwargs):
    """

    :param name:
    :param kwargs:
    :return:
    """

    env = Environment(loader=FileSystemLoader(
        environ.configs.make_path('resources', override_key='resources_path')
    ))

    return env.get_template(name).render(**kwargs)

