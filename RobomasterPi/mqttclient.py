
import socket
import paho.mqtt.client as mqtt
import uuid
import time
import config
import os
import function
from vision import vision

class MqttClient(mqtt.Client):

    def __init__(self):
        super().__init__()
        self.name = "NONAME"
        self.mac = self.get_mac()
        self.debug = True

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))
        system_topic = "FROM/SYSTEM/MESSAGE"
        topic = "TO/DEVICE/" + self.mac + "/MESSAGE"
        self.subscribe(topic, 0)
        self.subscribe(system_topic, 1)

        msg = "STATUS/CONNECT/" + config.TYPE + "/" + self.mac
        self.pub_sys_msg(msg)

    def on_message(self, mqttc, obj, msg):
        #socket.gethostbyname(socket.gethostname())
        #topicList = str(msg.topic).split('/')
        payload = str(msg.payload)
        payloadList = payload[2:len(payload) - 1].split('/')
        if self.debug == True:
            print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
            print("[0]:" + payloadList[0])
            print("[1]:" + payloadList[1])
            print("[2]:" + payloadList[2])
            print("[3]:" + payloadList[3])

        if payloadList[0] == 'INFO':
            if payloadList[1] == 'VERSION':
                msg = payloadList[0] + "/" + payloadList[1] + "/" + payloadList[2] + "/" + config.VERSION
                self.pub_msg(msg)
            elif payloadList[1] == 'NAME':
                if payloadList[2] == 'SET':
                    self.name = payloadList[3]
                msg = payloadList[0] + "/" + payloadList[1] + "/" + payloadList[2] + "/" + self.name
                self.pub_msg(msg)
            elif payloadList[1] == 'TYPE':
                if payloadList[2] == 'GET':
                    msg = payloadList[0] + "/" + payloadList[1] + "/" + payloadList[2] + "/" + config.TYPE
                    self.pub_msg(msg)
            elif payloadList[1] == 'IP':
                if payloadList[2] == 'GET':
                    msg = payloadList[0] + "/" + payloadList[1] + "/" + payloadList[2] + "/" + socket.gethostbyname(socket.gethostname())
                    self.pub_msg(msg)
        elif payloadList[0] == 'STATUS':
            if payloadList[1] == 'ALIVE':
                msg = payloadList[0] + "/" + payloadList[1] + "/" + config.TYPE + "/" + self.mac
                self.pub_sys_msg(msg)
        elif payloadList[0] == config.TYPE:
            if payloadList[1] == 'IMAGE':
                path = "temp.jpg"
                vision.write_img(path)
                self.pub_packet(path)
                msg = payloadList[0] + "/" + payloadList[1] + "/" + payloadList[2] + "/" + payloadList[3]
                self.pub_msg(msg)
                os.remove(path)        

    def on_publish(self, mqttc, obj, mid):
        if self.debug == True:
            print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        if self.debug == True:
            print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def try_connect(self):
        try:
            self.username_pw_set(config.MQTT_CONFIG['username'], config.MQTT_CONFIG['password'])
            self.connect(socket.gethostbyname(config.MQTT_CONFIG['host']), config.MQTT_CONFIG['port'])
            print('connect')
        except Exception as e:
            print('except: '+ str(e))
            raise Exception()

    def pub_sys_msg(self, msg):
        topic = "TO/SYSTEM/MESSAGE"
        self.publish(topic, msg, 0)
        if self.debug == True:
            print("Send[S]: " + str(msg))

    def pub_msg(self, msg):
        topic = "FROM/DEVICE/" + self.mac + "/MESSAGE"
        self.publish(topic, msg, 0)
        if self.debug == True:
            print("Send[N]: " + str(msg))
    
    def pub_packet(self, file):
        topic = "FROM/DEVICE/" + self.mac + "/PACKET"
        f = open(file, 'rb')
        self.publish(topic, bytearray(f.read()), 0)
        f.close()
        if self.debug == True:
            print("Send[N]: " + str(file))

    def get_mac(self):
        return hex(uuid.getnode())

    def thread_loop(self):
        rc = 0
        while True:
            self.try_connect()
            rc = 0
            while rc == 0:
                rc = self.loop()
            time.sleep(10)
        return rc

    def thread_start(self):
        function.asyncf(self.thread_loop)

mqttclient = MqttClient()
if __name__ == '__main__':
    print("start")
    try:
        mqttclient.try_connect()

        while True:
            mqttclient.loop()
    except KeyboardInterrupt:
        print("exit")