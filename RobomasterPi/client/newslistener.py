if __name__ == '__main__':
    from uclient import UClient
else:
    from .uclient import UClient
import time
PUSH_PORT: int = 40924

class NewsListener(UClient):

    def __init__(self):
        super().__init__()
        self.set_udp(True)

    def connectToRMS(self, ip):
        if self.is_opened():
            return True
        if ip == "":
            return False
        self.connect(ip, PUSH_PORT, 10)

    def on_recv(self, msg):
        print("News: " + str(msg))


newslistener = NewsListener()
if __name__ == '__main__':
    newslistener.connectToRMS("127.0.0.1")
    while True:
        time.sleep(1)