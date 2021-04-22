
import time
import threading

from client.commander import commander
import client.commander as cmd
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder
from vision.opencv import opencv
from vision.facerecognizer import FaceRecognizer
#sudo apt install python3-rpi.gpio
#sudo apt install python3-paho-mqtt
#sudo apt install python3-smbus
def init():
    print("init")
    finder = IPFinder()
    ip = finder.find_ip()
    commander.connectToRMS(ip)
    newslistener.connectToRMS(ip)
    eventlistener.connectToRMS(ip)
    #commander.stream(True)
    #opencv.open(ip)

def start():
    print("start")
    print(commander.get_robot_battery())
    commander.chassis_push_on(5,5,5)
    commander.gimbal_push_on()
    commander.enable_armor_event(True)
    commander.enable_sound_event(True)
    commander.robot_mode(cmd.MODE_FREE)
    commander.gimbal_recenter()
    commander.gimbal_speed(0,50)
    time.sleep(10)
    commander.gimbal_speed(0,-50)
    # commander.gimbal_recenter()
    # commander.robot_mode(cmd.MODE_CHASSIS_LEAD)
    # commander.chassis_move(5, 0, 0)
    # commander.chassis_wheel(0,0,0,0)
    # commander.chassis_move(0, 0, 180, 1, 100)
    #commander.chassis_move(5, 0, 0)
    #opencv.regist_face('heesung', 100)
    # recognizer = FaceRecognizer()
    # recognizer.train_from_file()
    # i = 0
    # while True:
    #     success, frame = opencv.grab()
    #     if not success:
    #         continue
    #     resize = opencv.rescale_frame(frame, 50)
    #     result, x, y = recognizer.face_recognize(resize)
    #     print("X: " + str(x) + " Y: " + str(y) + " " + str(i))
    #     #opencv.show("test", resize)
    #     i += 1
    #     opencv.delay(1)
        
    

def exit():
    #opencv.close()
    commander.stream(False)
    print("exit")

if __name__ == '__main__':
    init()
    start()
    exit()

