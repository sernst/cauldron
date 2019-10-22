import threading
import socket
import time
import webbrowser


class OpenUiOnStart(threading.Thread):

    def __init__(self, host: str, port: int):
        super(OpenUiOnStart, self).__init__()
        self.host = host or '127.0.0.1'
        self.port = port
        self.retries = 0

    @property
    def root_url(self):
        return 'http://{host}:{port}/'.format(host=self.host, port=self.port)

    def not_responding(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock.connect_ex((self.host, self.port))

    def run(self):
        while self.retries < 100:
            if self.not_responding():
                self.retries += 1
                time.sleep(0.25)
            else:
                webbrowser.open_new(self.root_url)
                break
