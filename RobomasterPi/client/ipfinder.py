
from .uclient import UClient 

IP_PORT: int = 40926
IP_MODULE_PORT: int = 40930

class IPFinder(UClient):
    def __init__(self):
        super().__init__()
        self.set_udp(True)
        self.thread_use(False)

    def find_robot_ip(self, timeout: float = None) -> str:
        
        self.connect("", IP_PORT, timeout)
        BROADCAST_INITIAL: str = 'robot ip '
        buffer, Addr = self.recv(timeout)
        self.close()
        if buffer is None:
            return ""
        if Addr is None:
            return ""
        ip = Addr[0]
        port = Addr[1]
        msg = buffer.decode()
        assert len(msg) > len(BROADCAST_INITIAL), f'broken msg from {ip}:{port}: {msg}'
        msg = msg[len(BROADCAST_INITIAL):]
        assert msg == ip, f'unmatched source({ip}) and reported IP({msg})'
        return msg

    def find_module_ip(self, timeout: float = None) -> str:
        
        self.connect("", IP_MODULE_PORT, timeout)
        BROADCAST_INITIAL: str = 'module ip '
        buffer, Addr = self.recv(timeout)
        self.close()
        if buffer is None:
            return ""
        if Addr is None:
            return ""
        ip = Addr[0]
        port = Addr[1]
        msg = buffer.decode()
        assert len(msg) > len(BROADCAST_INITIAL), f'broken msg from {ip}:{port}: {msg}'
        msg = msg[len(BROADCAST_INITIAL):]
        assert msg == ip, f'unmatched source({ip}) and reported IP({msg})'
        return msg


if __name__ == '__main__':
    finder = IPFinder()
    finder.find_robot_ip(1)
    