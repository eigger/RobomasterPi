import time
import function

from pixy2.pixy2 import Pixy2

class Controller(object):

    def __init__(self):
        self.pixy = Pixy2()
        

    def open(self):
        self.pixy.open()
        self.pixy.change_prog("Raspi")
        result, data = self.pixy.get_resolution()
        if result :
            self.frame_width = self.pixy.get_frame_width(data)
            self.frame_height = self.pixy.get_frame_height(data)
        #pixy.set_lamp (1, 0)

    def close(self):
        #pixy.set_lamp (0, 0)
        return


    def test(self):
        self.pixy.set_lamp (1, 0)
        time.sleep(1)
        self.pixy.set_lamp (0, 0)

    def get_offset(self):
        x_offset = 0
        y_offset = 0
        result, data = self.pixy.get_blocks(1, 1)
        if result:
            x_offset  = (self.frame_width / 2) - self.pixy.get_x_center(data)
            y_offset = self.pixy.get_y_center(data) - (self.frame_height / 2)
            print("x_offset = " + str(x_offset))
            print("y_offset = " + str(y_offset))
        return x_offset, y_offset

    def get_width_height(self):
        width = 0
        height = 0
        result, data = self.pixy.get_blocks(1, 1)
        if result:
            width  = self.pixy.get_width(data)
            height = self.pixy.get_height(data)
            print("width = " + str(width))
            print("height = " + str(height))
        return width, height

    def serach_object(self):
        width, height = self.get_width_height()

        return True

    def thread_loop(self):
        try:
            while True:
                
                search = True
                for i in range(0, 1):

                    if not self.serach_object():
                        search = False
                else:
                    print("NG")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("exit")

    def thread_start(self):
        function.asyncf(self.thread_loop)

controller = Controller()
if __name__ == '__main__':
    controller.open()
    controller.thread_loop()
    controller.close()
    
