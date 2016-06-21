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
    data = {}
    files = {}
    library_includes = []
    web_include_paths = project.settings.fetch('web_includes', []) + []

    for step in project.steps:
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

    add_bokeh(library_includes, files, web_includes)
    add_plotly(library_includes, files, web_includes)

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


def add_bokeh(library_includes, files, web_includes):
    """

    :param library_includes:
    :param files:
    :param web_includes:
    :return:
    """

    if 'bokeh' not in library_includes:
        return False

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
    files[file_path] = '\n'.join(contents)
    web_includes.append('/bokeh/bokeh.css')

    contents = []
    for p in br.js_files:
        with open(p, 'r+') as fp:
            contents.append(fp.read())
    file_path = os.path.join('bokeh', 'bokeh.js')
    files[file_path] = '\n'.join(contents)
    web_includes.append('/bokeh/bokeh.js')

    return True


def add_plotly(library_includes, files, web_includes):
    if 'plotly' not in library_includes:
        return False

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
    with open(p, 'r+') as f:
        contents = f.read()

    save_path = 'plotly/plotly.min.js'
    files[save_path] = contents
    web_includes.append('/{}'.format(save_path))

    return True
