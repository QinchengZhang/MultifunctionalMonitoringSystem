#coding:utf-8
import paho.mqtt.client as mqtt
import serial
import json
import time


class Sensor():
    data = 0
    ser = 0
    client = 0
    def __init__(self):
        self.data = {'temp' : 0,
                     'hum' : 0,
                     'PPM' : 0}
        
    def getDatabySerial(self,com):
        self.ser = serial.Serial('COM'+com)
        data = self.ser.readline()
        data = json.decoder(data)
        self.data = {'temp' : data['temp'],
                     'hum' : data['hum'],
                     'PPM' : data['PPM']}
        return self.data
    
    def MQTTServer(self, hostname, port, clientid):
        self.client = mqtt.Client(clientid)
        self.client.on_message = self.on_message
        self.client.connect(hostname,port,60)
        self.client.loop_forever()
    
    def getDatabyServer(self):
        return self.data
    
    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)     
        self.data = {'temp' : data['temp'],
                     'hum' : data['hum'],
                     'PPM' : data['PPM']}

