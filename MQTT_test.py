# coding=utf-8
import paho.mqtt.client as mqtt
import json


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 连接完成之后订阅gpio主题
    client.subscribe('MMS/devices/environment/')


# 消息推送回调函数
def on_message(client, userdata, msg):
    print(str(msg.topic) + " " + str(msg.payload))
    data = json.loads(msg.payload)
    print(data)


client = mqtt.Client(client_id='Win10')
client.on_connect = on_connect
client.on_message = on_message
client.connect('mq.tongxinmao.com', 18830, keepalive=60)
client.loop_forever()
