# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import serial
import json
import time


class Sensor(object):
    def __init__(self, com):
        try:
            self.ser = serial.Serial(com)
            self.isopened = True
        except serial.SerialException as e:
            self.isopened = False
        self.data = {'temp': 0,
                     'hum': 0,
                     'PPM': 0}

    def refindSensor(self, com):
        try:
            self.ser = serial.Serial(com)
            self.isopened = True
        except serial.SerialException as e:
            self.isopened = False

    def getDatabySerial(self):
        if self.isopened:
            data = self.ser.readline()
            data = json.loads(data)
            self.data = {'temp': data['temp'],
                         'hum': data['hum'],
                         'PPM': data['PPM']}
            return True, self.data
        else:
            return False, self.data

    def MQTTServer(self, hostname, port, clientid):
        self.client = mqtt.Client(clientid)
        self.client.on_message = self.on_message
        self.client.connect(hostname, port, 60)
        self.client.loop_forever()

    def getDatabyServer(self):
        return self.data

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        self.data = {'temp': data['temp'],
                     'hum': data['hum'],
                     'PPM': data['PPM']}
