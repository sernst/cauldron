import typing
import socket
import threading
import time
import webbrowser


def _check_usage(host: str, port: int) -> bool:
    """
    Checks to see whether or not the specified  port is utilized
    and returns a boolean indicating whether it is or not.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return not bool(sock.connect_ex((host, port)))


def find_open_port(
        host: str,
        ports: typing.Iterable[int]
) -> typing.Optional[int]:
    """
    Finds the first open port on the specified host that is not
    currently being utilized from the iterable containing possible
    port options and returns that value. If none of the ports are
    available a None value is returned.
    """
    return next((p for p in ports if not _check_usage(host, p)), None)


class OpenUiOnStart(threading.Thread):
    """
    Thread used to monitor the UI port for a point where the Flask
    web server is actively serving on the targeted port. When that
    occurs the UI is automatically opened in a new browser window.
    """

    def __init__(self, host: str, port: int):
        super(OpenUiOnStart, self).__init__()
        self.host = host or '127.0.0.1'
        self.port = port
        self.retries = 0

    @property
    def root_url(self) -> str:
        """URL of the UI to open when the UI app starts serving."""
        return 'http://{host}:{port}/'.format(host=self.host, port=self.port)

    def run(self):
        """
        Execution loop for the thread, which polls the UI port until
        it responds and then opens the UI in a web browser when that
        happens. The polling process will last up to 25 seconds after
        which it will give up.
        """
        while self.retries < 100:
            if _check_usage(self.host, self.port):
                webbrowser.open_new(self.root_url)
                break
            else:
                self.retries += 1
                time.sleep(0.25)
