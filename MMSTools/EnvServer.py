# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import serial
import json
import time


class EnvServer(object):

    def __init__(self, hostname, port, clientid):
        self.data = {'temp': 0,
                     'hum': 0,
                     'PPM': 0}
        self.client = mqtt.Client(clientid)
        self.client.on_message = self.on_message
        self.client.connect(hostname, port, 60)
        self.client.subscribe('MMS/devices/environment/')
        self.client.loop_forever()

    def getData(self):
        return self.data

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        self.data = {'temp': data['temp'],
                     'hum': data['hum'],
                     'PPM': data['PPM']}
