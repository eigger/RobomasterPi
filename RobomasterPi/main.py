
import time
import threading

from mqttclient import mqttclient
from commander import commander
import commander as cmd
from eventlistener import eventlistener
from newslistener import newslistener

#sudo apt install python3-rpi.gpio
#sudo apt install python3-paho-mqtt
#sudo apt install python3-smbus
def init():
    print("init")
    commander.open()
    ip = commander.get_ip()
    newslistener.set_ip(ip)
    eventlistener.set_ip(ip)

def start():
    print("start")
    newslistener.thread_start()
    eventlistener.thread_start()
    commander.gimbal_push_on()
    commander.armor_event(cmd.ARMOR_HIT, True)
    commander.sound_event(cmd.SOUND_APPLAUSE, True)
    

def exit():
    while True:
        time.sleep(1)
    print("exit")

if __name__ == '__main__':
    init()
    start()
    exit()

