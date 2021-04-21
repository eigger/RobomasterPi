import socket
import time
import threading

class UClient(object):

    def __init__(self):
        self._opend: bool = False
        self._ip: str = ""
        self._port: int = 0
        self._timeout: float = 30
        self._buffer_size = 512
        self._thread_use = True
        self._udp = False

    def connect(self, ip: str = None, port: int = None, timeout: float = None):
        if self._opend:
            return True
        try:
            print("Try connect")
            if ip is not None:
                self._ip = ip
            if port is not None:
                self._port = port
            if timeout is not None:
                self._timeout = timeout
            
            if self._udp:
                self._conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._conn.settimeout(self._timeout)
                self._conn.bind((self._ip, self._port))
            else:
                self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._conn.settimeout(self._timeout)
                self._conn.connect((self._ip, self._port))
            self._opend = True
            if self._thread_use:
                self.__asyncf__(self.recv_loop)
            print("Connected: " + str(self._ip) + " " + str(self._port))
        except:
            self._opend = False
        return self._opend

    def close(self):
        if not self._opend:
            return True
        # self._conn.shutdown(SHUT_RDWR)
        self._conn.close()
        self._opend = False
        print("Disconnected")

    def is_opened(self):
        return self._opend

    def thread_use(self, use):
        self._thread_use = use

    def set_udp(self, use):
        self._udp = use

    def recv(self, timeout):
        self._conn.settimeout(timeout)
        try:
            if self._udp:
                buffer, Addr = self._conn.recvfrom(self._buffer_size)
                return buffer, Addr
            else:
                buffer = self._conn.recv(self._buffer_size)
                return buffer, None
        except Exception as e:
            print(e)
        return None, None
        

    def recv_loop(self):
        while True:
            buffer, Addr = self.recv(None)
            if buffer is None:
                break
            if len(buffer) == 0:
                break
            self.on_recv(buffer)
        self.close()
            
    def send(self, msg):
        if not self._opend:
            if not self.connect():
                return False
        try:
            self._conn.send(msg.encode())
            print("Send: " + str(msg))
        except:
            return False
        return True

    def on_recv(self, buffer):
        print("Recv: " + str(buffer.decode()))

    def __asyncf__(self, func, *args):
        thread = threading.Thread(target=func, args=(args))
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    client = UClient()
    client.connect("127.0.0.1", 3456, 5)
    while True:
        client.send("test")
        time.sleep(5)
