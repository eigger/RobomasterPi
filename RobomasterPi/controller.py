import time
import function

from client.interfacer import interfacer
from client.commander import commander
import client.commander as cmd
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder

class Controller(object):

    def __init__(self):
        self.finder = IPFinder()
        

    def open(self):
        ip = self.finder.find_robot_ip()
        commander.connectToRMS(ip)
        newslistener.connectToRMS(ip)
        eventlistener.connectToRMS(ip)

        # ip = self.finder.find_module_ip()
        # interfacer.connectToModule(ip)
        # resolution = interfacer.get_resolution()
        # if len(resolution) > 0:
        #     self.frame_width = int(resolution[0])
        #     self.frame_height = int(resolution[1])

        # print(self.frame_width)
        # print(self.frame_height)
        

    def close(self):
        commander.close()
        newslistener.close()
        eventlistener.close()
        interfacer.close()
        #pixy.set_lamp (0, 0)
        return

    def get_offset(self):
        x_offset = 0
        y_offset = 0
        blocks = interfacer.get_blocks(1, 1)
        if len(blocks) > 2:
            x = int(blocks[1])
            y = int(blocks[2])
            if x and y:
                x_offset  = x - (self.frame_width / 2)
                y_offset =  (self.frame_height / 2) - y
                print("x_offset = " + str(x_offset))
                print("y_offset = " + str(y_offset))
                #self.pixy.set_lamp(1, 1)
                return True, x_offset, y_offset

        #self.pixy.set_lamp(0, 0)
        return False, 0, 0

    def thread_loop(self):
        print(commander.get_robot_battery())
        # commander.gimbal_push_on()
        # commander.enable_armor_event(True)
        # commander.enable_sound_event(True)
        # commander.robot_mode(cmd.MODE_FREE)
        # commander.gimbal_recenter()
        commander.pwm_freq(1, 1000)
        commander.pwm_value(1, 10)
        time.sleep(5)

        commander.pwm_value(1, 90)
        time.sleep(1)

        return
        try:
            while True:
                
                result, x, y = self.get_offset()
                if result :
                    commander.gimbal_speed(y, x)
                else:
                    commander.gimbal_speed(0, 0)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("exit")

    def thread_start(self):
        function.asyncf(self.thread_loop)

controller = Controller()
if __name__ == '__main__':
    controller.open()
    controller.thread_loop()
    controller.close()
    
