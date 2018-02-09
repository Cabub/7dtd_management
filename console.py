from threading import Thread
from queue import Queue, Empty
import time
import socket


_BUFFER_SIZE = 1024
_server_line_split = '\r\n'
_server_strip_chars = ['\x00']


class Console:
    _sock = None
    _r_thread = None
    _w_thread = None
    _r_queue = Queue()
    _w_queue = Queue()
    _stop_signal = False
    _logged_in = False

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._sock = socket.socket()
        self._sock.connect((host, port))
        self._r_thread = Thread(
            target=self._console_reader
        )
        self._w_thread = Thread(
            target=self._console_writer
        )
        self._r_thread.start()
        self._w_thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def _console_writer(self):
        while True:
            try:
                cmd = self._w_queue.get(timeout=1)
                if cmd != '':
                    self._sock.send((cmd + '\r\n').encode())
            except Empty:
                pass  # I don't care
            if self._stop_signal:
                break

    def _console_reader(self):
        last_line = ''
        while True:
            # read data from the socket
            data = self._sock.recv(_BUFFER_SIZE)
            if data == b'' or self._stop_signal:
                break
            # separate into lines
            data = data.decode()
            for chars in _server_strip_chars:
                data = data.strip(chars)
            data = last_line + data
            lines = data.split(_server_line_split)
            last_line = lines[-1]
            lines = filter(lambda x: x != '', lines[:-1])
            # add each line to the output queue
            for line in lines:
                self._r_queue.put(line)

    def send_command(self, cmd):
        if not self._logged_in:
            # TODO update to use logging module
            print('you need to log in first')
        self._w_queue.put(cmd)

    def flush_log(self):
        log = list()
        while self._r_queue.qsize():
            log.append(self._r_queue.get())
        return log

    def log_in(self, password):
        if not self._logged_in:
            self._w_queue.put(password)
            self._logged_in = True
            self.flush_log()
        else:
            # TODO update to use logging module
            print("you're already logged in")

    def cleanup(self):
        self._logged_in = False
        self._stop_signal = True
        self._w_thread.join()
        self._r_thread.join()
        self._sock.close()
