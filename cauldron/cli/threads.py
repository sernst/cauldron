import threading
import uuid


class CauldronThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        """
        """

        super(CauldronThread, self).__init__(*args, **kwargs)
        self.abort = False
        self.daemon = True
        self.uid = str(uuid.uuid4())
        self.command = None
        self.parser = None
        self.kwargs = None
        self.result = None
        self.response = None

    def run(self):
        """
        """

        self.result = self.command(
            parser=self.parser,
            response=self.response,
            **self.kwargs
        )


def abort_thread():
    """
    This function checks to see if the user has indicated that they want the
    currently running execution to stop prematurely by marking the running
    thread as aborted. It only applies to operations that are run within
    CauldronThreads and not the main thread.

    :return:
    """

    thread = threading.current_thread()

    if not isinstance(thread, CauldronThread):
        return

    if thread.abort:
        raise RuntimeError('User Aborted Execution')
