from threading import Thread
from queue import Queue, Empty
import socket


_BUFFER_SIZE = 1024
_server_line_split = '\r\n'
_server_strip_chars = ['\x00']


class NotLoggedIn(RuntimeError):
    pass


class AlreadyLoggedIn(RuntimeError):
    pass


class Destroyed(RuntimeError):
    pass


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
        self._sock.settimeout(1)
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
            try:
                data = self._sock.recv(_BUFFER_SIZE)
            except socket.timeout as e:
                continue
            except OSError as e:
                break
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
            raise NotLoggedIn('you need to log in first')
        if self._stop_signal:
            raise Destroyed('this console has already been destroyed')
        self._w_queue.put(cmd)

    def feed(self):
        while not self._stop_signal:
            yield self._r_queue.get()

    def get_line(self, timeout=.5):
        if not self._stop_signal:
            return self._r_queue.get(timeout)

    def flush_log(self):
        if self._stop_signal:
            raise Destroyed('this console has already been destroyed')
        log = list()
        while self._r_queue.qsize():
            log.append(self._r_queue.get())
        return log

    def log_in(self, password):
        if self._stop_signal:
            raise Destroyed('this console has already been destroyed')
        if not self._logged_in:
            self._w_queue.put(password)
            self._logged_in = True
            self.flush_log()
        else:
            raise AlreadyLoggedIn("you're already logged in")

    def cleanup(self):
        if self._stop_signal:
            raise Destroyed('this console has already been destroyed')
        self._logged_in = False
        self._stop_signal = True
        self._sock.close()
        self._w_thread.join()
        self._r_thread.join()
