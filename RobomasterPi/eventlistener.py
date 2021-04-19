import socket
import function
import time
EVENT_PORT: int = 40925

class EventListener(object):

    def __init__(self):
        self._closed: bool = False

    def set_ip(self, ip: str = ''):
        self._ip: str = ip

    def open(self, ip: str = '', timeout: float = 30):

        try:
            self._ip: str = ip
            self._closed: bool = False
            self._timeout: float = timeout
            self._conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._conn.settimeout(timeout)
            self._conn.connect((self._ip, EVENT_PORT))
            self._opend: bool = True
        except Exception as e:
            self._opend: bool = False

        return self._opend

        
    def thread_loop(self):
        while True:
            if self.open(self._ip):
                while True:
                    try:
                        data, addr = self._conn.recvfrom(1024)
                        print("Event : " + str(data))
                    except Exception as e:
                        break
            else:
                time.sleep(1)

        
    def thread_start(self):
        function.asyncf(self.thread_loop)


eventlistener = EventListener()
if __name__ == '__main__':
    eventlistener.thread_loop()
