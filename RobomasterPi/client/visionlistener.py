if __name__ == '__main__':
    from uclient import UClient
else:
    from .uclient import UClient
import time
VIDEO_PORT: int = 40921

class VisionListener(UClient):

    def __init__(self):
        super().__init__()

    def connectToRMS(self, ip):
        if self.is_opened():
            return True
        if ip == "":
            return False
        self.connect(ip, VIDEO_PORT, 10)

    # def on_recv(self, msg):
    #     pass


visionlistener = VisionListener()
if __name__ == '__main__':
    visionlistener.connectToRMS("127.0.0.1")
    while True:
        time.sleep(1)
