import time
import function

from client.interfacer import interfacer
from client.commander import commander
import client.commander as cmd
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder
from client.visionlistener import visionlistener
from vision.opencv import opencv

import numpy as np
import cv2

STEP_INIT = 0
STEP_WAIT = 1
STEP_PIXY = 2
STEP_OPENCV = 3
class Controller(object):
    
    def __init__(self):
        self.MAX_SERVO_COUNT = 4
        self.servo_position = [0 for i in range(self.MAX_SERVO_COUNT)]
        self.finder = IPFinder()
        self.opened = False
        self.module_opened = False
        self.vision_opened = False
        self.battery = 0
        self.battery_timer = time.time()
        self.step = STEP_INIT
        self.robot_ip = ""
        self.module_ip = ""
        self._bytes = bytes()
        
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
        visionlistener.connectToRMS(self.robot_ip)
        visionlistener.set_callback(self.vision_push)
        # time.sleep(1)
        # opencv.open(self.robot_ip)

    def close(self):
        commander.close()
        newslistener.close()
        eventlistener.close()
        
        
    def close_module(self):
        interfacer.close()

    def close_vision(self):
        # opencv.close()
        visionlistener.close()

    def event_push(self, buffer):
        params = buffer.decode().split(' ')
        print(params)

    def news_push(self, buffer):
        params = buffer.decode().split(' ')
        print(params)

    def vision_push(self, buffer):
        try :
            width = 1280
            height = 720
            if len(buffer) >= 512:
                self._bytes = self._bytes + buffer
                print("len : " + str(len(self._bytes)))
                if len(self._bytes) >= width * height * 3:
                    in_frame = (
                        np
                        .frombuffer(self._bytes, np.uint8)
                        .reshape([height, width, 3])
                    )

                    self._bytes = bytes()
                    cv2.imshow("frame", in_frame)

                    #Display the frame
                    cv2.waitKey(1) 
        except Exception as e:
            self._bytes = bytes()
            print('except: ' + str(e))


    def thread_loop(self):
        self.initializeRMS()
        # commander.gimbal_moveto(20)
        # commander.blaster_fire()
        # commander.chassis_move(0.1)
        # commander.chassis_move(-0.1)
        # commander.chassis_move(0, 0.3)
        # commander.chassis_move(0, -0.3)
        # commander.robot_mode(cmd.MODE_CHASSIS_LEAD)
        # commander.chassis_move(0, 0, 50)
        # commander.chassis_move(0, 0, -50)
        # commander.robot_mode(cmd.MODE_GIMBAL_LEAD)
        # commander.gimbal_moveto(20, 20)
        # commander.gimbal_moveto(20, -20)
        # commander.robot_mode(cmd.MODE_FREE)

        self.step = STEP_WAIT
        pos = -200

        while True:
            
            if self.check_low_bettery() :
                break
            if self.step == STEP_INIT:

                self.step = STEP_WAIT
            elif self.step == STEP_WAIT:

                self.step = STEP_WAIT
            elif self.step == STEP_PIXY:
                self.trace_object_pixy2()
                self.step = STEP_PIXY

            elif self.step == STEP_OPENCV:
                commander.gimbal_moveto(20, pos)
                time.sleep(0.5)
                pos += 10
                if pos > 200:
                    pos = -200
                self.step = STEP_OPENCV

            time.sleep(1)

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

    def servo_move_to(self, id, position):
        self.servo_position[id] = float(position)
        print("servo " + str(id) + " : " + str(self.servo_position[id]))
        mask = 1 << id
        commander.pwm_value(mask, self.servo_position[id])

    def servo_multi_move_to(self, idlist, poslist):

        for i in range(0, len(idlist)):
            self.servo_move_to(idlist[i], poslist[i])

    def servo_move(self, id, position):
        self.servo_move_to(id, self.servo_position[id] + float(position))

    def servo_get_position(self, id):
        return self.servo_position[id]

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
    controller.close_vision()
    controller.close()
    
