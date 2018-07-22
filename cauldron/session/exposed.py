import os
import time
import typing
from datetime import datetime

from cauldron import environ
from cauldron import templating
from cauldron.cli import threads
from cauldron.render import stack as render_stack
from cauldron.runner.python_file import UserAbortError
from cauldron.session import projects
from cauldron.session import report
from cauldron.session.caching import SharedCache


class ExposedProject(object):
    """
    A simplified form of the project for exposure to Cauldron users. A
    single exposed project is created when the Cauldron library is first
    imported and that exposed project is accessible from the cauldron
    root module.
    """

    def __init__(self):
        self._project = None  # type: projects.Project

    @property
    def internal_project(self) -> typing.Union[projects.Project, None]:
        """
        The current Cauldron project that is represented by this object.
        The value will be None if no project has been loaded.
        """
        return self._project

    @property
    def id(self) -> typing.Union[str, None]:
        """Identifier for the project."""
        return self._project.id if self._project else None

    @property
    def display(self) -> typing.Union[None, report.Report]:
        """The display report for the current project."""
        return (
            self._project.current_step.report
            if self._project and self._project.current_step else
            None
        )

    @property
    def shared(self) -> typing.Union[None, SharedCache]:
        """The shared display object associated with this project."""
        return self._project.shared if self._project else None

    @property
    def settings(self) -> typing.Union[None, SharedCache]:
        """The settings associated with this project."""
        return self._project.settings if self._project else None

    @property
    def title(self) -> typing.Union[None, str]:
        """The title of this project."""
        return self._project.title if self._project else None

    @title.setter
    def title(self, value: typing.Union[None, str]):
        """
        Modifies the title of the project, which is initially loaded from the
        `cauldron.json` file.
        """
        if not self._project:
            raise RuntimeError('Failed to assign title to an unloaded project')
        self._project.title = value

    def load(self, project: typing.Union[projects.Project, None]):
        """Connects this object to the specified source project."""
        self._project = project

    def unload(self):
        """Disconnects this object from the specified source project."""
        self._project = None

    def path(self, *args: typing.List[str]) -> typing.Union[None, str]:
        """
        Creates an absolute path in the project source directory from the
        relative path components.

        :param args:
            Relative components for creating a path within the project source
            directory
        :return:
            An absolute path to the specified file or directory within the
            project source directory.
        """
        if not self._project:
            return None

        return environ.paths.clean(os.path.join(
            self._project.source_directory,
            *args
        ))

    def stop(self, message: str = None, silent: bool = False):
        """
        Stops the execution of the project at the current step immediately
        without raising an error. Use this to abort running the project in
        situations where some critical branching action should prevent the
        project from continuing to run.

        :param message:
            A custom display message to include in the display for the stop
            action. This message is ignored if silent is set to True.
        :param silent:
            When True nothing will be shown in the notebook display when the
            step is stopped. When False, the notebook display will include
            information relating to the stopped action.
        """
        me = self.get_internal_project()
        if not me or not me.current_step:
            return

        if not silent:
            render_stop_display(me.current_step, message)
        raise UserAbortError(halt=True)

    def get_internal_project(
            self,
            timeout: float = 1
    ) -> typing.Union['projects.Project', None]:
        """
        Attempts to return the internally loaded project. This function
        prevents race condition issues where projects are loaded via threads
        because the internal loop will try to continuously load the internal
        project until it is available or until the timeout is reached.

        :param timeout:
            Maximum number of seconds to wait before giving up and returning
            None.
        """
        count = int(timeout / 0.1)
        for _ in range(count):
            project = self.internal_project
            if project:
                return project
            time.sleep(0.1)

        return self.internal_project


class ExposedStep(object):
    """
    A simplified form of a ProjectStep that is exposed to the for Cauldron
    users.
    """

    @property
    def _step(self) -> typing.Union[None, 'projects.ProjectStep']:
        """
        Internal access to the source step. Should not be used outside
        of Cauldron development.

        :return:
            The ProjectStep instance that this ExposedStep represents
        """
        import cauldron
        try:
            return cauldron.project.get_internal_project().current_step
        except Exception:
            return None

    @property
    def start_time(self) -> typing.Union[datetime, None]:
        """
        The time at which the step started running. If the step has never run
        this value will be `None`.
        """
        return self._step.start_time

    @property
    def end_time(self) -> typing.Union[datetime, None]:
        """
        The time at which the step stopped running. If the step has never run
        or is currently running, this value will be `None`.
        """
        return self._step.end_time

    @property
    def elapsed_time(self) -> float:
        """
        The number of seconds that has elapsed since the step started running
        if the step is still running. Or, if the step has already finished
        running, the amount of time that elapsed during the last execution of
        the step.
        """
        return self._step.elapsed_time

    @property
    def visible(self) -> bool:
        """
        Whether or not this step will be visible in the display after it
        has finished running. Steps are always visible while running or
        if they fail to run due to an error. However, if this is set to
        False, once the step completes successfully it will no longer be
        visible in the display.
        """
        return self._step.is_visible

    @visible.setter
    def visible(self, value: bool):
        """Setter for the visible property."""
        self._step.is_visible = value

    def stop(
            self,
            message: str = None,
            silent: bool = False,
            halt: bool = False
    ):
        """
        Stops the execution of the current step immediately without raising
        an error. Use this to abort the step running process if you want
        to return early.

        :param message:
            A custom display message to include in the display for the stop
            action. This message is ignored if silent is set to True.
        :param silent:
            When True nothing will be shown in the notebook display when the
            step is stopped. When False, the notebook display will include
            information relating to the stopped action.
        :param halt:
            Whether or not to keep running other steps in the project after
            this step has been stopped. By default this is False and after this
            stops running, future steps in the project will continue running
            if they've been queued to run. If you want stop execution entirely,
            set this value to True and the current run command will be aborted
            entirely.
        """
        step = self._step
        if not step:
            return

        if not silent:
            render_stop_display(step, message)
        raise UserAbortError(halt=halt)

    def breathe(self):
        """
        Checks the current execution state for the running step and responds
        to any changes in that state. Particular useful for checking to see
        if a step has been aborted by the user during long-running executions.
        """
        if self._step:
            threads.abort_thread()

    def write_to_console(self, message: str):
        """
        Writes the specified message to the console stdout without including
        it in the notebook display.
        """
        if not self._step:
            raise ValueError(
                'Cannot write to the console stdout on an uninitialized step'
            )
        interceptor = self._step.report.stdout_interceptor
        interceptor.write_source('{}'.format(message))

    def render_to_console(self, message: str, **kwargs):
        """
        Renders the specified message to the console using Jinja2 template
        rendering with the kwargs as render variables. The message will also
        be dedented prior to rendering in the same fashion as other Cauldron
        template rendering actions.

        :param message:
            Template string to be rendered.
        :param kwargs:
            Variables to be used in rendering the template.
        """
        rendered = templating.render(message, **kwargs)
        return self.write_to_console(rendered)


def render_stop_display(step: 'projects.ProjectStep', message: str):
    """Renders a stop action to the Cauldron display."""
    stack = render_stack.get_formatted_stack_frame(
        project=step.project,
        error_stack=False
    )

    try:
        names = [frame['filename'] for frame in stack]
        index = names.index(os.path.realpath(__file__))
        frame = stack[index - 1]
    except Exception:
        frame = {}

    stop_message = (
        '{}'.format(message)
        if message else
        'This step was explicitly stopped prior to its completion'
    )

    dom = templating.render_template(
        'step-stop.html',
        message=stop_message,
        frame=frame
    )
    step.report.append_body(dom)
