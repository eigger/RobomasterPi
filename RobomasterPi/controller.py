import time
import function

from pixy2.pixy2 import Pixy2
from client.commander import commander
import client.commander as cmd
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder

class Controller(object):

    def __init__(self):
        self.pixy = Pixy2()
        

    def open(self):
        self.pixy.open()
        self.pixy.change_prog("Raspi")
        result, data = self.pixy.get_resolution()
        if result and len(data) > 0:
            self.frame_width = self.pixy.get_frame_width(data)
            self.frame_height = self.pixy.get_frame_height(data)

        print(self.frame_width)
        print(self.frame_height)
        finder = IPFinder()
        ip = finder.find_robot_ip()
        commander.connectToRMS(ip)
        newslistener.connectToRMS(ip)
        eventlistener.connectToRMS(ip)
        

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
        if result and len(data) > 0:
            x = self.pixy.get_x_center(data)
            y = self.pixy.get_y_center(data)
            if x and y:
                x_offset  = x - (self.frame_width / 2)
                y_offset =  (self.frame_height / 2) - y
                print("x_offset = " + str(x_offset))
                print("y_offset = " + str(y_offset))
                #self.pixy.set_lamp(1, 1)
                return True, x_offset, y_offset

        #self.pixy.set_lamp(0, 0)
        return False, 0, 0

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
        print(commander.get_robot_battery())
        commander.gimbal_push_on()
        commander.enable_armor_event(True)
        commander.enable_sound_event(True)
        commander.robot_mode(cmd.MODE_FREE)
        commander.gimbal_recenter()
        try:
            while True:
                
                result, x, y = self.get_offset()
                if result :
                    commander.gimbal_speed(y, x)
                else:
                    commander.gimbal_speed(0, 0)
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("exit")

    def thread_start(self):
        function.asyncf(self.thread_loop)

controller = Controller()
if __name__ == '__main__':
    controller.open()
    controller.thread_loop()
    controller.close()
    
