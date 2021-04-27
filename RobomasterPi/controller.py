import time
import function

from client.interfacer import interfacer
from client.commander import commander
import client.commander as cmd
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder
from vision.opencv import opencv
STEP_INIT = 0
STEP_WAIT = 1
STEP_PIXY = 2
STEP_OPENCV = 3
class Controller(object):

    def __init__(self):
        self.finder = IPFinder()
        self.opened = False
        self.module_opened = False
        self.vision_opened = False
        self.battery = 0
        self.battery_timer = time.time()
        self.step = STEP_INIT
        self.robot_ip = ""
        self.module_ip = ""
        
    def open(self):
        self.robot_ip = self.finder.find_robot_ip()
        commander.connectToRMS(self.robot_ip)
        newslistener.connectToRMS(self.robot_ip)
        eventlistener.connectToRMS(self.robot_ip)
        newslistener.set_callback(self.news_push)
        eventlistener.set_callback(self.event_push)
        self.opened = True

    def open_module(self):
        self.module_ip = self.finder.find_module_ip()
        interfacer.connectToModule(self.module_ip)
        resolution = interfacer.get_resolution()
        if len(resolution) > 0:
            self.frame_width = int(resolution[0])
            self.frame_height = int(resolution[1])

        print(self.frame_width)
        print(self.frame_height)
        self.module_opened = True

    def open_vision(self):
        commander.stream(True)
        # time.sleep(1)
        # opencv.open(self.robot_ip)

    def close(self):
        commander.close()
        newslistener.close()
        eventlistener.close()
        
    def close_module(self):
        interfacer.close()

    def close_vision(self):
        opencv.close()

    def event_push(self, buffer):
        params = buffer.decode().split(' ')
        print(params)

    def news_push(self, buffer):
        params = buffer.decode().split(' ')
        print(params)

    def thread_loop(self):
        self.initializeRMS()
        commander.gimbal_moveto(20)
        self.step = STEP_WAIT
        pos = -200

        while True:
            
            if self.check_low_bettery() :
                break
            if self.step == STEP_INIT:

                self.step = STEP_WAIT
            elif self.step == STEP_WAIT:

                self.step = STEP_OPENCV
            elif self.step == STEP_PIXY:
                self.trace_object_pixy2()
                self.step = STEP_PIXY

            elif self.step == STEP_OPENCV:
                # commander.gimbal_moveto(20, pos, 500, 500)
                # time.sleep(0.5)
                # pos += 10
                # if pos > 200:
                #     pos = -200
                # img = opencv.get_image()
                # opencv.show("frame", img)
                opencv.delay(1)
                self.step = STEP_OPENCV

            # time.sleep(1)

    def thread_start(self):
        function.asyncf(self.thread_loop)

    def initializeRMS(self):
        commander.gimbal_push_on()
        commander.enable_armor_event(True)
        commander.enable_sound_event(True)
        commander.robot_mode(cmd.MODE_FREE)
        commander.gimbal_recenter()

    def check_low_bettery(self):
        if time.time() - self.battery_timer < 30:
            return False
        self.battery_timer = time.time()
        self.battery = commander.get_robot_battery()
        print("Battery: " + str(self.battery))
        if self.battery < 10:
            return True
        return False

    def trace_object_pixy2(self):
        result, x, y = self.get_offset()
        if result :
            commander.gimbal_speed(y, x)
        else:
            commander.gimbal_speed(0, 0)

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

controller = Controller()
if __name__ == '__main__':
    controller.open()
    controller.open_vision()
    controller.thread_loop()
    controller.close()
    
