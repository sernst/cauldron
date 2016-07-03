import os
import shutil
import glob
import json

from cauldron import environ
from cauldron.session import projects
from cauldron import templating

try:
    from bokeh.resources import Resources as BokehResources
except Exception:
    BokehResources = None

try:
    from plotly.offline import offline as plotly_offline
except Exception:
    plotly_offline = None


def write_project(project: 'projects.Project'):
    """

    :param project:
    :return:
    """

    environ.systems.remove(project.output_directory)
    os.makedirs(project.output_directory)

    has_error = False
    head = []
    body = []
    data = dict()
    files = dict()
    file_copies = dict()
    library_includes = []
    web_include_paths = project.settings.fetch('web_includes', []) + []

    for step in project.steps:
        if step.is_muted:
            continue

        has_error = has_error or step.error
        report = step.report
        body.append(step.dumps())
        data.update(report.data.fetch(None))
        files.update(report.files.fetch(None))
        web_include_paths += step.web_includes
        library_includes += step.report.library_includes

    dependency_bodies = []
    dependency_errors = []
    for dep in project.dependencies:
        dependency_bodies.append(dep.dumps())
        if dep.error:
            has_error = True
            dependency_errors.append(dep.error)

    if dependency_bodies:
        body.insert(0, templating.render_template(
            'dependencies.html',
            body=''.join(dependency_bodies)
        ))

    if dependency_errors:
        body.insert(0, ''.join(dependency_errors))

    web_includes = []
    for item in web_include_paths:
        # Copy "included" files and folders that were specified in the
        # project file to the output directory

        source_path = environ.paths.clean(
            os.path.join(project.source_directory, item)
        )
        if not os.path.exists(source_path):
            continue

        item_path = os.path.join(project.output_directory, item)
        output_directory = os.path.dirname(item_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, item_path)
            glob_path = os.path.join(item_path, '**', '*')
            for entry in glob.iglob(glob_path, recursive=True):
                web_includes.append(
                    '{}'.format(
                        entry[len(project.output_directory):]
                            .replace('\\', '/'))
                )
        else:
            shutil.copy2(source_path, item_path)
            web_includes.append('/{}'.format(item.replace('\\', '/')))

    add_components(library_includes, file_copies, files, web_includes)

    for filename, source_path in file_copies.items():
        file_path = os.path.join(project.output_directory, filename)
        output_directory = os.path.dirname(file_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        shutil.copy2(source_path, file_path)

    for filename, contents in files.items():
        file_path = os.path.join(project.output_directory, filename)
        output_directory = os.path.dirname(file_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(file_path, 'w+') as f:
            f.write(contents)

    with open(project.output_path, 'w+') as f:
        # Write the results file
        f.write(templating.render_template(
            'report.js.template',
            DATA=json.dumps({
                'data': data,
                'includes': web_includes,
                'settings': project.settings.fetch(None),
                'body': '\n'.join(body),
                'head': '\n'.join(head),
                'has_error': has_error
            })
        ))

    copy_assets(project)


def copy_assets(project: 'projects.Project'):
    """

    :param project:
    :return:
    """

    directory = os.path.join(project.source_directory, 'assets')
    if not os.path.exists(directory):
        return False

    output_directory = os.path.join(project.output_directory, 'assets')
    shutil.copytree(directory, output_directory)
    return True


def add_components(library_includes, file_copies, file_writes, web_includes):
    """

    :param library_includes:
    :param file_copies:
    :param file_writes:
    :param web_includes:
    :return:
    """

    for lib_name in set(library_includes):
        if lib_name == 'bokeh':
            add_bokeh(file_writes, web_includes)
        elif lib_name == 'plotly':
            add_plotly(file_copies, web_includes)
        else:
            add_global_component(lib_name, web_includes)


def add_global_component(name, web_includes):
    """

    :param name:
    :param web_includes:
    :return:
    """

    component_directory = environ.paths.resources(
        'web', 'components', name
    )

    if not os.path.exists(component_directory):
        return False

    glob_path = '{}/**/*'.format(component_directory)
    for path in glob.iglob(glob_path, recursive=True):
        if not os.path.isfile(path):
            continue

        if not path.endswith('.css') and not path.endswith('.js'):
            continue

        slug = path[len(component_directory):]

        # web includes that start with a : are relative to the root
        # results folder, not the project itself. They are for shared
        # resource files
        web_includes.append(':components/{}{}'.format(name, slug))

    return True


def add_component(name, file_copies, web_includes):
    """

    :param name:
    :param file_copies:
    :param web_includes:
    :return:
    """

    component_directory = environ.paths.resources(
        'web', 'components', name
    )

    if not os.path.exists(component_directory):
        return False

    glob_path = '{}/**/*'.format(component_directory)
    for path in glob.iglob(glob_path, recursive=True):
        if not os.path.isfile(path):
            continue

        slug = path[len(component_directory):]
        save_path = 'components/{}'.format(slug)
        file_copies[save_path] = path

        if path.endswith('.js') or path.endswith('.css'):
            web_includes.append('/{}'.format(save_path))

    return True


def add_bokeh(file_writes, web_includes):
    """

    :param file_writes:
    :param web_includes:
    :return:
    """

    if BokehResources is None:
        environ.log(
            """
            [WARNING]: Bokeh library is not installed. Unable to
                include library dependencies, which may result in
                HTML rendering errors. To resolve this make sure
                you have installed the Bokeh library.
            """
        )
        return False

    br = BokehResources(mode='absolute')

    contents = []
    for p in br.css_files:
        with open(p, 'r+') as fp:
            contents.append(fp.read())
    file_path = os.path.join('bokeh', 'bokeh.css')
    file_writes[file_path] = '\n'.join(contents)
    web_includes.append('/bokeh/bokeh.css')

    contents = []
    for p in br.js_files:
        with open(p, 'r+') as fp:
            contents.append(fp.read())
    file_path = os.path.join('bokeh', 'bokeh.js')
    file_writes[file_path] = '\n'.join(contents)
    web_includes.append('/bokeh/bokeh.js')

    return True


def add_plotly(file_copies, web_includes):
    """

    :param file_copies:
    :param web_includes:
    :return:
    """

    if plotly_offline is None:
        environ.log(
            """
            [WARNING]: Plotly library is not installed. Unable to
                include library dependencies, which may result in
                HTML rendering errors. To resolve this make sure
                you have installed the Plotly library.
            """
        )
        return False

    p = os.path.join(
        environ.paths.clean(os.path.dirname(plotly_offline.__file__)),
        'plotly.min.js'
    )

    save_path = 'components/plotly/plotly.min.js'
    file_copies[save_path] = p
    web_includes.append('/{}'.format(save_path))

    return True
