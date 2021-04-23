from uclient import UClient 
import time
import multiprocessing as mp
from ipfinder import IPFinder
CTX = mp.get_context('spawn')
MODULE_PORT: int = 40931

class Interfacer(UClient):

    def __init__(self):
        super().__init__()
        self.thread_use(False)
        self.set_udp(False)
        self._mu: mp.Lock = CTX.Lock()

    def connectToModule(self, ip):
        if self.is_opened():
            return True
        if ip == "":
            return False
        self.connect(ip, MODULE_PORT, 10)

    def _do(self, *args) -> str:
        assert len(args) > 0, 'empty arg not accepted'
        cmd = ':'.join(map(str, args)) + '\r\n'
        self.send(cmd)
        print("Send: " + str(cmd))
        buf, addr = self.recv(60)
        print("Recv: " + str(buf))
        return buf.decode().strip('\r\n')
    
    def get_ip(self) -> str:
        return self._ip

    def do(self, *args) -> str:
        with self._mu:
            return self._do(*args)

    def get_version(self) -> str:
        return (self.do('INFO', 'VERSION', ''))


interfacer = Interfacer()
if __name__ == '__main__':
    finder = IPFinder()
    ip = finder.find_module_ip()
    interfacer.connectToModule(ip)
    interfacer.get_version()
    while True:
        time.sleep(1)
        break