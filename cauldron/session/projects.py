import functools
import json
import os
import sys
import time
import typing
import hashlib

from cauldron import environ
from cauldron import render
from cauldron import templating
from cauldron.session import definitions
from cauldron.session import writing
from cauldron.session.caching import SharedCache
from cauldron.session.report import Report
from cauldron.session import naming

DEFAULT_SCHEME = 'S{{##}}-{{name}}.{{ext}}'


class ProjectStep(object):
    """
    A computational step within the project, which contains data and
    functionality related specifically to that step as well as a reference to
    the project itself.
    """

    _reference_index = 0

    def __init__(
            self,
            project: 'Project' = None,
            definition: definitions.FileDefinition = None
    ):
        """

        :param project:
        :param definition:
        """

        self.__class__._reference_index += 1
        self._reference_id = '{}'.format(self.__class__._reference_index)

        self.definition = definition if definition is not None else dict()
        self.project = project
        self.report = Report(self)

        self.last_modified = None
        self.code = None
        self.is_running = False
        self._is_dirty = True
        self.error = None
        self.is_muted = False
        self.dom = None  # type: dict
        self.progress_message = None
        self.sub_progress_message = None
        self.progress = 0
        self.sub_progress = 0
        self.test_locals = None  # type: dict

    @property
    def reference_id(self):
        return self._reference_id

    @property
    def uuid(self):
        """

        :return:
        """

        return hashlib.sha1(self.source_path.encode()).hexdigest()

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
    def source_path(self) -> typing.Union[None, str]:
        if not self.project or not self.report:
            return None
        return os.path.join(self.project.source_directory, self.filename)

    def kernel_serialize(self):
        """

        :return:
        """

        return dict(
            uuid=self.uuid,
            reference_id=self.reference_id,
            name=self.definition.name,
            slug=self.definition.slug,
            index=self.index,
            source_path=self.source_path,
            last_modified=self.last_modified,
            last_display_update=self.report.last_update_time,
            is_dirty=self.is_dirty(),
            status=self.status(),
            exploded_name=naming.explode_filename(
                self.definition.name,
                self.project.naming_scheme
            )
        )

    def status(self):
        """

        :return:
        """

        is_dirty = self.is_dirty()

        return dict(
            uuid=self.uuid,
            reference_id=self.reference_id,
            name=self.definition.name,
            muted=self.is_muted,
            last_modified=self.last_modified,
            last_display_update=self.report.last_update_time,
            dirty=is_dirty,
            is_dirty=is_dirty,
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

    def get_dom(self) -> dict:
        """ Retrieves the current value of the DOM for the step """

        if self.is_running:
            return self.dumps()

        if self.dom is not None:
            return self.dom

        dom = self.dumps()
        self.dom = dom
        return dom

    def dumps(self) -> dict:
        """

        :return:
        """

        code_file_path = os.path.join(
            self.project.source_directory,
            self.filename
        )
        code = dict(
            filename=self.filename,
            path=code_file_path,
            code=render.code_file(code_file_path)
        )

        if not self.is_running:
            # If no longer running, make sure to flush the stdout buffer so
            # any print statements at the end of the step get included in
            # the body
            self.report.flush_stdout()

        # Create a copy of the body for dumping
        body = self.report.body[:]

        if self.is_running:
            # If still running add a temporary copy of anything not flushed
            # from the stdout buffer to the copy of the body for display. Do
            # not flush the buffer though until the step is done running or
            # it gets flushed by another display call.
            body.append(self.report.read_stdout())

        body = ''.join(body)

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

        std_err = (
            self.report.read_stderr()
            if self.is_running else
            self.report.flush_stderr()
        ).strip('\n').rstrip()

        dom = templating.render_template(
            'step-body.html',
            last_display_update=self.report.last_update_time,
            code=code,
            body=body,
            has_body=has_body,
            id=self.definition.name,
            title=self.report.title,
            subtitle=self.report.subtitle,
            summary=self.report.summary,
            error=self.error,
            index=self.index,
            is_running=self.is_running,
            progress_message=self.progress_message,
            progress=int(round(max(0, min(100, 100 * self.progress)))),
            sub_progress_message=self.sub_progress_message,
            sub_progress=int(round(max(0, min(100, 100 * self.sub_progress)))),
            std_err=std_err
        )

        if not self.is_running:
            self.dom = dom
        return dom


class Project:
    """

    """

    def __init__(
            self,
            source_directory: str,
            results_path: str = None,
            shared: typing.Union[dict, SharedCache] = None
    ):
        """
        :param source_directory:
        :param results_path:
            [optional] The path where the results files for the project will
            be saved. If omitted, the default global results path will be
            used.
        :param shared:
            [optional] The shared data cache used to store project data when
            run
        """

        source_directory = environ.paths.clean(source_directory)
        if os.path.isfile(source_directory):
            source_directory = os.path.dirname(source_directory)
        self.source_directory = source_directory

        self.steps = []  # type: typing.List[ProjectStep]
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
    def uuid(self):
        """

        :return:
        """

        return hashlib.sha1(self.source_path.encode()).hexdigest()

    @property
    def library_directories(self):
        def listify(value):
            return [value] if isinstance(value, str) else list(value)
        folders = listify(self.settings.fetch('library_folders', ['libs']))

        return [
            environ.paths.clean(os.path.join(self.source_directory, folder))
            for folder in folders
        ]

    @property
    def asset_directories(self):
        def listify(value):
            return [value] if isinstance(value, str) else list(value)
        folders = listify(self.settings.fetch('asset_folders', ['assets']))

        return [
            environ.paths.clean(os.path.join(self.source_directory, folder))
            for folder in folders
        ]

    @property
    def has_error(self):
        """

        :return:
        """

        for s in self.steps:
            if s.error:
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
        return self.settings.fetch('id', 'unknown')

    @property
    def naming_scheme(self) -> str:
        return self.settings.fetch('naming_scheme', None)

    @naming_scheme.setter
    def naming_scheme(self, value: typing.Union[str, None]):
        self.settings.put(naming_scheme=value)

    @property
    def current_step(self) -> typing.Union[ProjectStep, None]:
        if len(self.steps) < 1:
            return None

        step = self._current_step
        return step if step else self.steps[0]

    @current_step.setter
    def current_step(self, value: typing.Union[Report, None]):
        self._current_step = value

    @property
    def source_path(self) -> typing.Union[None, str]:
        directory = self.source_directory
        return os.path.join(directory, 'cauldron.json') if directory else None

    @property
    def results_path(self) -> str:
        """The path where the project results will be written"""

        def possible_paths():
            yield self._results_path
            yield self.settings.fetch('path_results')
            yield environ.configs.fetch('results_directory')
            yield environ.paths.results(self.uuid)

        return next(p for p in possible_paths() if p is not None)

    @results_path.setter
    def results_path(self, value: str):
        self._results_path = environ.paths.clean(value)

    @property
    def url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        :return:
        """

        return 'file://{path}?id={id}'.format(
            path=os.path.join(self.results_path, 'project.html'),
            id=self.uuid
        )

    @property
    def baked_url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        with the loading information baked into the file so that no URL
        parameters are needed to view it, which is needed on platforms like
        windows
        """

        return 'file://{path}'.format(
            path=os.path.join(self.results_path, 'display.html'),
            id=self.uuid
        )

    @property
    def output_directory(self) -> str:
        """
        Returns the directory where the project results files will be written
        :return:
        """

        return os.path.join(self.results_path, 'reports', self.uuid, 'latest')

    @property
    def output_path(self) -> str:
        """
        Returns the full path to where the results.js file will be written
        :return:
        """

        return os.path.join(self.output_directory, 'results.js')

    def make_remote_url(self, host: str = None):
        """

        :param host:
        :return:
        """

        if host:
            host = host.rstrip('/')
        else:
            host = ''

        return '{}/view/project.html?id={}'.format(host, self.uuid)

    def snapshot_path(self, *args: typing.Tuple[str]) -> str:
        """

        :param args:
        :return:
        """

        return os.path.join(self.output_directory, '..', 'snapshots', *args)

    def snapshot_url(self, snapshot_name: str) -> typing.Union[None, str]:
        """

        :param snapshot_name:
        :return:
        """

        url = self.url
        if url is None:
            return None

        return '{}&sid={}'.format(self.url, snapshot_name)

    def kernel_serialize(self):
        """

        :return:
        """

        return dict(
            uuid=self.uuid,
            serial_time=time.time(),
            last_modified=self.last_modified,
            source_directory=self.source_directory,
            source_path=self.source_path,
            output_directory=self.output_directory,
            output_path=self.output_path,
            url=self.url,
            remote_slug=self.make_remote_url(),
            title=self.title,
            id=self.id,
            steps=[s.kernel_serialize() for s in self.steps],
            naming_scheme=self.naming_scheme
        )

    def refresh(self, force: bool = False) -> bool:
        """
        Loads the cauldron.json configuration file for the project and populates
        the project with the loaded data. Any existing data will be overwritten,
        including previously stored ProjectSteps.

        If the project has already loaded with the most recent version of the
        cauldron.json file, this method will return without making any changes
        to the project.

        :param force:
            If true the project will be refreshed even if the project file
            modified timestamp doesn't indicate that it needs to be refreshed.
        :return:
            Whether or not a refresh was needed and carried out
        """

        lm = self.last_modified
        if not force and lm is not None and lm >= os.path.getmtime(self.source_path):
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

        self.last_modified = time.time()
        return True

    def get_step(self, name: str) -> ProjectStep:
        """

        :param name:
        :return:
        """

        for s in self.steps:
            if s.definition.name == name:
                return s

        return None

    def get_step_by_reference_id(self, reference_id: str) -> ProjectStep:
        """

        :param reference_id:
        :return:
        """

        for s in self.steps:
            if s.reference_id == reference_id:
                return s

        return None

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
            steps=[ps.definition.serialize() for ps in self.steps]
        )

        data = self.settings.fetch(None)
        with open(path, 'w+') as f:
            json.dump(data, f, indent=2, sort_keys=True)

        self.last_modified = time.time()

    def write(self) -> str:
        """

        :return:
        """

        writing.save(self)
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
        raise FileNotFoundError('No project file found at: {}'.format(path))

    with open(path, 'r') as f:
        out = json.load(f)

    project_folder = os.path.split(os.path.dirname(path))[-1]
    if 'id' not in out or not out['id']:
        out['id'] = project_folder

    return out
