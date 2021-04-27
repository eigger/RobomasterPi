if __name__ == '__main__':
    from uclient import UClient
else:
    from .uclient import UClient
import time
EVENT_PORT: int = 40925

class EventListener(UClient):

    def __init__(self):
        super().__init__()

    def connectToRMS(self, ip):
        if self.is_opened():
            return True
        if ip == "":
            return False
        self.connect(ip, EVENT_PORT, 10)

    def on_recv(self, msg):
        print("Event: " + str(msg))


eventlistener = EventListener()
if __name__ == '__main__':
    eventlistener.connectToRMS("127.0.0.1")
    while True:
        time.sleep(1)
