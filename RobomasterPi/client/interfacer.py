if __name__ == '__main__':
    from uclient import UClient
else:
    from .uclient import UClient
import time
import multiprocessing as mp
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
        return buf.decode().strip('\n').strip('\r')
    
    def get_ip(self) -> str:
        return self._ip

    def do(self, *args) -> str:
        with self._mu:
            return self._do(*args)

    def get_version(self) -> str:
        resp = self.do('INFO', 'VERSION', '')
        return resp.split(':')[3]

    def get_blocks(self, sigmap, max_blocks):
        resp = self.do('PIXY', 'GET', 'BLOCKS', str(sigmap) + ',' + str(max_blocks))
        return resp.split(':')[3].split(',')

    def get_resolution(self):
        resp = self.do('PIXY', 'GET', 'RESOLUTION')
        return resp.split(':')[3].split(',')


interfacer = Interfacer()
if __name__ == '__main__':
    print(interfacer.get_version())
    while True:
        time.sleep(1)
        break