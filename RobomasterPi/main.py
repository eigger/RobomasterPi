
import time
import threading

from client.commander import commander
from client.eventlistener import eventlistener
from client.newslistener import newslistener
from client.ipfinder import IPFinder
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

def start():
    print("start")
    commander.gimbal_push_on()
    commander.enable_armor_event(True)
    commander.enable_sound_event(True)
    

def exit():
    while True:
        time.sleep(1)
    print("exit")

if __name__ == '__main__':
    init()
    start()
    exit()

