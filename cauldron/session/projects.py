import functools
import json
import os
import sys
import time
import typing

from cauldron import environ
from cauldron import render
from cauldron import templating
from cauldron.session import definitions
from cauldron.session import writing
from cauldron.session.caching import SharedCache
from cauldron.session.report import Report


class ProjectStep(object):
    """
    A computational step within the project, which contains data and
    functionality related specifically to that step as well as a reference to
    the project itself.
    """

    def __init__(
            self,
            project: 'Project' = None,
            definition: definitions.FileDefinition = None
    ):
        self.definition = definition
        self.project = project
        self.report = Report(self)
        self.last_modified = None
        self.code = None
        self._is_dirty = True
        self.error = None
        self.is_muted = False

    @property
    def filename(self) -> str:
        return self.definition.slug

    @property
    def web_includes(self) -> list:
        if not self.project:
            return []

        out = []
        for fn in self.definition.get('web_includes', []):
            out.append(os.path.join(
                self.definition.get('folder', ''),
                fn.replace('/', os.sep)
            ))
        return out

    @property
    def index(self) -> int:
        if not self.project:
            return -1
        return self.project.steps.index(self)

    @property
    def source_path(self) -> str:
        if not self.project or not self.report:
            return None
        return os.path.join(self.project.source_directory, self.filename)

    def kernel_serialize(self):
        """

        :return:
        """

        return dict(
            name=self.definition.name,
            slug=self.definition.slug,
            index=self.index,
            source_path=self.source_path,
            last_modified=self.last_modified,
            is_dirty=self.is_dirty(),
            status=self.status()
        )

    def status(self):
        """

        :return:
        """

        return dict(
            name=self.definition.name,
            muted=self.is_muted,
            last_modified=self.last_modified,
            dirty=self.is_dirty(),
            run=self.last_modified is not None,
            error=self.error is not None
        )

    def is_dirty(self):
        """

        :return:
        """
        if self._is_dirty:
            return self._is_dirty

        if self.last_modified is None:
            return True
        p = self.source_path
        if not p:
            return False
        return os.path.getmtime(p) >= self.last_modified

    def mark_dirty(self, value):
        """

        :param value:
        :return:
        """

        self._is_dirty = bool(value)

    def dumps(self):
        """

        :return:
        """

        code_file_path = os.path.join(
            self.project.source_directory,
            self.filename
        )
        codes = [dict(
            filename=self.filename,
            path=code_file_path,
            code=render.code_file(code_file_path)
        )]

        for fn in self.definition.get('web_includes', []):
            fn_path = os.path.join(
                self.project.source_directory,
                self.definition.get('folder', ''),
                fn.replace('/', os.sep)
            )

            codes.append(dict(
                filename=fn,
                path=fn_path,
                code=render.code_file(fn_path)
            ))

        body = ''.join(self.report.body)
        has_body = len(body) > 0 and (
            body.find('<div') != -1 or
            body.find('<span') != -1 or
            body.find('<p') != -1 or
            body.find('<pre') != -1 or
            body.find('<h') != -1 or
            body.find('<ol') != -1 or
            body.find('<ul') != -1 or
            body.find('<li') != -1
        )

        return templating.render_template(
            'step-body.html',
            codes=codes,
            body=body,
            has_body=has_body,
            id=self.definition.name,
            title=self.report.title,
            subtitle=self.report.subtitle,
            summary=self.report.summary,
            error=self.error
        )


class ProjectDependency(object):
    """

    """

    def __init__(
            self,
            project: 'Project' = None,
            definition: definitions.FileDefinition = None
    ):
        self.definition = definition
        self.project = project
        self.last_modified = None
        self._is_dirty = True
        self.error = None
        self.is_muted = False

    @property
    def id(self) -> str:
        if not self.definition:
            return None
        return self.definition.get('name', 'unknown')

    @property
    def filename(self) -> str:
        return os.path.join(
            self.definition.get('folder', ''),
            self.definition.get('file', '')
        )

    @property
    def source_path(self) -> str:
        if not self.project:
            return None
        return os.path.join(self.project.source_directory, self.filename)

    def kernel_serialize(self):
        """

        :return:
        """

        return dict(
            name=self.definition.name,
            slug=self.definition.slug,
            source_path=self.source_path,
            last_modified=self.last_modified,
            is_dirty=self.is_dirty()
        )

    def is_dirty(self):
        """

        :return:
        """
        if self._is_dirty:
            return self._is_dirty

        if self.last_modified is None:
            return True
        p = self.source_path
        if not p:
            return False
        return os.path.getmtime(p) >= self.last_modified

    def mark_dirty(self, value):
        """

        :param value:
        :return:
        """

        self._is_dirty = bool(value)

    def dumps(self):
        """

        :return:
        """

        code_file_path = os.path.join(
            self.project.source_directory,
            self.filename
        )

        return templating.render_template(
            'project-dependency.html',
            code=render.code_file(code_file_path),
            path=code_file_path,
            filename=self.filename,
            id=self.definition.name,
            title=self.definition.get('title', self.definition.get('name')),
            subtitle=self.definition.get('subtitle'),
            summary=self.definition.get('summary')
        )


class Project(object):

    def __init__(
            self,
            source_directory: str,
            results_path: str = None,
            identifier: str = None,
            shared: typing.Union[dict, SharedCache] = None
    ):
        """
        :param source_directory:
        :param results_path:
            [optional] The path where the results files for the project will
            be saved. If omitted, the default global results path will be
            used.
        :param identifier:
            [optional] The project unique identifier. If omitted, the
            identifier will be loaded from the settings file, or assigned
        :param shared:
            [optional] The shared data cache used to store project data when
            run
        """

        source_directory = environ.paths.clean(source_directory)
        if os.path.isfile(source_directory):
            source_directory = os.path.dirname(source_directory)
        self.source_directory = source_directory

        self.steps = []  # type: typing.List[ProjectStep]
        self.dependencies = []  # type: typing.List[ProjectDependency]
        self._results_path = results_path  # type: str
        self._current_step = None  # type: ProjectStep
        self.last_modified = None

        def as_shared_cache(source):
            if source is None:
                return SharedCache()
            if not hasattr(source, 'fetch'):
                return SharedCache().put(**source)
            return source

        self.shared = as_shared_cache(shared)
        self.settings = SharedCache()
        self.refresh()

    @property
    def library_directory(self):
        """

        :return:
        """

        return os.path.join(self.source_directory, 'libs')

    @property
    def has_error(self):
        """

        :return:
        """

        for s in self.steps:
            if s.error:
                return True
        for d in self.dependencies:
            if d.error:
                return True
        return False

    @property
    def title(self) -> str:
        out = self.settings.fetch('title')
        if out:
            return out
        out = self.settings.fetch('name')
        if out:
            return out
        return self.id

    @title.setter
    def title(self, value: str):
        self.settings.title = value

    @property
    def id(self) -> str:
        if self.settings:
            return self.settings.fetch('id', 'unknown')
        return 'unknown'

    @property
    def current_step(self) -> ProjectStep:
        if self._current_step:
            return self._current_step
        return self.steps[0] if self.steps else None

    @current_step.setter
    def current_step(self, value: typing.Union[Report, None]):
        self._current_step = value

    @property
    def source_path(self) -> str:
        if not self.source_directory:
            return None
        return os.path.join(self.source_directory, 'cauldron.json')

    @property
    def results_path(self) -> str:
        if self._results_path:
            return self._results_path

        if self.settings and self.settings['path_results']:
            return self.settings['path_results']

        return environ.configs.make_path(
            'results',
            override_key='results_path'
        )

    @results_path.setter
    def results_path(self, value: str):
        self._results_path = environ.paths.clean(value)

    @property
    def url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        :return:
        """

        if not self.results_path:
            return None

        return 'file://{path}?id={id}'.format(
            path=os.path.join(self.results_path, 'project.html'),
            id=self.id
        )

    @property
    def output_directory(self) -> str:
        """
        Returns the directory where the project results files will be written
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.results_path, 'reports', self.id, 'latest')

    @property
    def output_path(self) -> str:
        """
        Returns the full path to where the results.js file will be written
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.output_directory, 'results.js')

    def snapshot_path(self, *args: typing.Tuple[str]) -> str:
        """

        :param args:
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.output_directory, '..', 'snapshots', *args)

    def snapshot_url(self, snapshot_name: str) -> str:
        """

        :param snapshot_name:
        :return:
        """

        return '{}&sid={}'.format(self.url, snapshot_name)

    def kernel_serialize(self):
        """

        :return:
        """

        return dict(
            serial_time=time.time(),
            last_modified=self.last_modified,
            source_directory=self.source_directory,
            source_path=self.source_path,
            output_directory=self.output_directory,
            output_path=self.output_path,
            url=self.url,
            title=self.title,
            id=self.id,
            steps=[s.kernel_serialize() for s in self.steps],
            dependencies=[d.kernel_serialize() for d in self.dependencies]
        )

    def refresh(self) -> bool:
        """
        Loads the cauldron.json configuration file for the project and populates
        the project with the loaded data. Any existing data will be overwritten,
        including previously stored ProjectSteps.

        If the project has already loaded with the most recent version of the
        cauldron.json file, this method will return without making any changes
        to the project.

        :return:
            Whether or not a refresh was needed and carried out
        """

        lm = self.last_modified
        if lm is not None and lm >= os.path.getmtime(self.source_path):
            return False

        self.settings.clear().put(
            **load_project_settings(self.source_directory)
        )

        path = self.settings.fetch('results_path')
        if path:
            self.results_path = environ.paths.clean(
                os.path.join(self.source_directory, path)
            )

        python_paths = self.settings.fetch('python_paths', [])
        if isinstance(python_paths, str):
            python_paths = [python_paths]
        for path in python_paths:
            path = environ.paths.clean(
                os.path.join(self.source_directory, path)
            )
            if path not in sys.path:
                sys.path.append(path)

        self.steps = []
        for step_data in self.settings.fetch('steps', []):
            self.add_step(step_data)

        self.dependencies = []
        for dep_data in self.settings.fetch('dependencies', []):
            self.add_dependency(dep_data)

        self.last_modified = time.time()
        return True

    def add_dependency(
            self,
            dependency_data: typing.Union[str, dict],
    ) -> ProjectDependency:
        """

        :param dependency_data:
        :return:
        """

        fd = definitions.FileDefinition(
            data=dependency_data,
            project=self,
            project_folder=functools.partial(
                self.settings.fetch,
                'dependencies_folder'
            )
        )

        if not fd.name:
            self.last_modified = 0
            return None

        dep = ProjectDependency(self, fd)
        self.dependencies.append(dep)
        self.last_modified = time.time()
        return dep

    def index_of_step(self, name) -> int:
        """

        :param name:
        :return:
        """

        name = name.strip('"')

        for index, s in enumerate(self.steps):
            if s.definition.name == name:
                return int(index)

        return None

    def add_step(
            self,
            step_data: typing.Union[str, dict],
            index: int = None
    ) -> ProjectStep:
        """

        :param step_data:
        :param index:
        :return:
        """

        fd = definitions.FileDefinition(
            data=step_data,
            project=self,
            project_folder=functools.partial(
                self.settings.fetch,
                'steps_folder'
            )
        )

        if not fd.name:
            self.last_modified = 0
            return None

        ps = ProjectStep(self, fd)

        if index is None:
            self.steps.append(ps)
        else:
            if index < 0:
                index %= len(self.steps)
            self.steps.insert(index, ps)

            if fd.name.endswith('.py'):
                for i in range(self.steps.index(ps) + 1, len(self.steps)):
                    self.steps[i].mark_dirty(True)

        self.last_modified = time.time()
        return ps

    def remove_step(self, name) -> 'ProjectStep':
        """

        :param name:
        :return:
        """

        step = None

        for ps in self.steps:
            if ps.definition.name == name:
                step = ps
                break

        if step is None:
            return None

        if step.definition.name.endswith('.py'):
            for i in range(self.steps.index(step) + 1, len(self.steps)):
                self.steps[i].mark_dirty(True)

        self.steps.remove(step)

        return step

    def save(self, path: str = None):
        """

        :param path:
        :return:
        """

        if not path:
            path = self.source_path

        self.settings.put(
            steps=[ps.definition.serialize() for ps in self.steps],
            dependencies=[pd.definition.serialize() for pd in self.dependencies]
        )

        data = self.settings.fetch(None)
        with open(path, 'w+') as f:
            json.dump(data, f, indent=2, sort_keys=True)

        self.last_modified = time.time()

    def write(self) -> str:
        """

        :return:
        """

        writing.write_project(self)
        return self.url

    def status(self) -> dict:

        return dict(
            id=self.id,
            steps=[s.status() for s in self.steps],
            last_modified=self.last_modified
        )


def load_project_settings(path: str) -> dict:
    """

    :param path:
    :return:
    """

    path = environ.paths.clean(path)
    if os.path.isdir(path):
        path = os.path.join(path, 'cauldron.json')
    if not os.path.exists(path):
        raise FileNotFoundError(
            'No project file found at: {}'.format(path)
        )
    with open(path, 'r+') as f:
        out = json.load(f)

    project_folder = os.path.split(os.path.dirname(path))[-1]
    if 'id' not in out or not out['id']:
        out['id'] = project_folder

    return out
