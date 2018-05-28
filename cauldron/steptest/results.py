from cauldron import environ
from cauldron.session import projects
from cauldron.session.caching import SharedCache


class StepTestRunResult:
    """
    This class contains information returned from running a step during testing.
    """

    def __init__(
            self,
            step: 'projects.ProjectStep',
            response: 'environ.Response'
    ):
        self._step = step  # type: projects.ProjectStep
        self._response = response  # type: environ.Response
        self._locals = SharedCache().put(**step.test_locals)

    @property
    def local(self) -> SharedCache:
        """
        Container object that holds all of the local variables that were
        defined within the run step
        """

        return self._locals

    @property
    def success(self) -> bool:
        """
        Whether or not the step was successfully run. This value will be
        False if there as an uncaught exception during the execution of the
        step.
        """

        return not self._response.failed

    def echo_error(self) -> str:
        """
        Creates a string representation of the exception that cause the step
        to fail if an exception occurred. Otherwise, an empty string is returned.

        :return:
            The string representation of the exception that caused the running
            step to fail or a blank string if no exception occurred
        """

        if not self._response.errors:
            return ''

        return '{}'.format(self._response.errors[0].serialize())