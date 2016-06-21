import os
import shutil
import typing

from cauldron import environ
from cauldron.session import projects
from cauldron.session.caching import SharedCache
from cauldron.session import report


class ExposedProject(object):
    """
    A simplified form of the project for exposure to Cauldron users. A
    single exposed project is created when the Cauldron library is first
    imported and that exposed project is accessible from the cauldron
    root module.
    """

    def __init__(self):
        self._project = None

    @property
    def internal_project(self) -> projects.Project:
        """

        :return:
        """

        return self._project

    @property
    def display(self) -> report.Report:
        """

        :return:
        """

        if not self._project or not self._project.current_step:
            return None
        return self._project.current_step.report

    @property
    def shared(self) -> SharedCache:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.shared

    @property
    def settings(self) -> SharedCache:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.settings

    @property
    def title(self) -> str:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.title

    @title.setter
    def title(self, value: str):
        """

        :param value:
        :return:
        """

        if not self._project:
            raise RuntimeError('Failed to assign title to an unloaded project')
        self._project.title = value

    def load(self, project: typing.Union[projects.Project, None]):
        """

        :param project:
        :return:
        """

        self._project = project


def initialize_results_path(results_path: str):
    """

    :param results_path:
    :return:
    """

    def remove(target_path):
        if not os.path.exists(target_path):
            return True

        caller = shutil.rmtree if os.path.isdir(target_path) else os.remove
        try:
            caller(target_path)
            return True
        except Exception:
            try:
                caller(target_path)
                return True
            except Exception:
                pass

        return False

    dest_path = environ.paths.clean(results_path)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    web_src_path = environ.paths.resources('web')
    for item in os.listdir(web_src_path):
        item_path = os.path.join(web_src_path, item)
        out_path = os.path.join(dest_path, item)

        remove(out_path)

        if os.path.isdir(item_path):
            shutil.copytree(item_path, out_path)
        else:
            shutil.copy2(item_path, out_path)
