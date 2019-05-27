from MMSTools import Sensor

ser = Sensor.Sensor(3)
while True:
    _, data = ser.getDatabySerial()
    print(type(data['hum']))
