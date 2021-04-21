import time
import function

import pixy2.pixy as pixy
from ctypes import *
from pixy2.pixy import *

class Controller(object):

    def __init__(self):
        pass
        

    def open(self):
        pixy.init()
        pixy.change_prog ("Raspi")
        #pixy.set_lamp (1, 0)

    def close(self):
        #pixy.set_lamp (0, 0)
        return


    def test(self):
        pixy.set_lamp (1, 0)
        time.sleep(1)
        pixy.set_lamp (0, 0)

    def get_offset(self):
        blocks = BlockArray(1)
        count = pixy.ccc_get_blocks(1, blocks)
        print("Count = " + str(count))
        x_offset = 0
        y_offset = 0
        if count > 0:
            for index in range (0, count):
                x_offset  = (pixy.get_frame_width () / 2) - blocks[index].m_x
                y_offset = blocks[index].m_y - (pixy.get_frame_height () / 2)
                print("x_offset = " + str(x_offset))
                print("y_offset = " + str(y_offset))
        return count, x_offset, y_offset

    def get_width_height(self):
        blocks = BlockArray(1)
        count = pixy.ccc_get_blocks(1, blocks)
        width = 0
        height = 0
        print("Count = " + str(count))
        if count > 0:
            for index in range (0, count):
                width  = blocks[index].m_width
                height = blocks[index].m_height
                print("width = " + str(width))
                print("height = " + str(height))
        return count, width, height

    def serach_object(self):
        count, width, height = self.get_width_height()

        if count == 1:
            return False

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
    
