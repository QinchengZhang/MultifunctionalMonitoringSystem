# 引入需要用到的库
import serial, time
import datetime as dt
import numpy as np
import cv2
import binascii
import re


class Thermal(object):
    def __init__(self, com):
        self.t0 = time.time()
        self.Tmax = 40
        self.Tmin = 20
        self.ser = serial.Serial(com)
        self.ser.baudrate = 460800
        self.ser.write(serial.to_bytes([0xA5, 0x15, 0x03, 0xBD]))

        time.sleep(0.1)

        self.ser.write(serial.to_bytes([0xA5, 0x25, 0x04, 0xCE]))
        time.sleep(0.1)

        # Starting automatic data colection
        self.ser.write(serial.to_bytes([0xA5, 0x35, 0x02, 0xDC]))
        time.sleep(0.1)

        self.ser.write(serial.to_bytes([0xA5, 0x45, 0x5F, 0x49]))
        time.sleep(0.1)

    # 获取MLX90640的数据发射率
    def get_emissivity(self):
        self.ser.write(serial.to_bytes([0xA5, 0x55, 0x01, 0xFB]))
        read = self.ser.read(4)
        return read[2] / 100

        # 获取温度矩阵函数

    def get_temp_array(self, d):
        d = str(d, encoding='utf-8')
        # getting ambient temperature
        T_a = (int(d[3080:3082], 16) + int(d[3082:3084], 16) * 256) / 100
        # getting raw array of pixels temperature
        raw_data = re.findall(r'.{4}', d[8:3080])

        T_array = np.asarray(raw_data)
        return T_a, T_array

        # 将温度矩阵转换为像素矩阵函数

    def td_to_image(self, f):
        array = []
        for i in f:
            low = int(i[0:2], 16)
            high = int(i[2:4], 16)
            temp = (high * 256 + low) / 13
            array.append(temp)
        array = np.asarray(array, dtype=np.uint8)
        array.shape = (24, 32)
        return array

    def transoform(self, image):
        min = image.min()
        max = image.max()
        img = ((image - min) / (max - min)) * 255
        array = np.asarray(img, dtype=np.uint8)
        return array

    def getImage(self):
        head = binascii.hexlify(self.ser.read(2))
        while str(head, encoding='utf=8') != '5a5a':
            head = binascii.hexlify(self.ser.read(2))
        # waiting for data frame
        data = head + binascii.hexlify(self.ser.read(1542))

        # The data is ready, let's handle it!
        Ta, temp_array = self.get_temp_array(data)
        ta_img = self.td_to_image(temp_array)
        min = ta_img.min()
        max = ta_img.max()
        # Image processing
        img = self.transoform(ta_img)
        # print(img, img.min(), img.max())
        img = cv2.GaussianBlur(img, (3, 3), 0)
        font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
        img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_CUBIC)
        cv2.putText(img, 'MIN_TEMP:{:.2f} MAX_TEMP:{:.2f} TA_TEMP:{:.2f}'.format(min, max, Ta), (0, 15), font, 0.5,
                    (255, 255, 255), 1)
        return True, img
