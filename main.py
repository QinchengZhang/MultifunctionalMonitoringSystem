# -*- coding: utf-8 -*
import time

import cv2
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MMSTools import Sensor
from MMSTools import CameraDevice
from MMSTools import Thermal


class WorkThread(QThread):
    sinOut = pyqtSignal(int)
    client = mqtt.Client(client_id='Win10')

    def __int__(self):
        super(WorkThread, self).__init__()

    def run(self):
        # 消息推送回调函数
        self.client = mqtt.Client(client_id='Win10')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect('123.56.0.232', 61613, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # 连接完成之后订阅gpio主题
        client.subscribe("devices/environment/")

    def on_message(self, client, userdata, msg):
        print(str(msg.topic) + " " + str(msg.payload))
        self.sinOut.emit(msg.payload)  # 反馈信号出去


class MyGUI(QtWidgets.QWidget):
    menubar = 0
    icon = 0
    left_layout = 0
    mid_layout = 0
    right_layout = 0
    left_box = 0
    mid_box = 0
    right_box = 0
    timerCamera = 0
    cameraDevice = 0
    therimgDevice = 0
    cameraWidget = 0
    therimgWidget = 0
    sensor = 0
    temp_area = 0
    hum_area = 0
    PPM_area = 0

    def __init__(self):
        self.aip = CameraDevice.FacesOps()
        self.thermal = Thermal.Thermal(3)
        super(MyGUI, self).__init__()
        self.initUI()

    def initUI(self):
        # ICON设置
        self.icon = QIcon("./imgs/cdmc.png")
        self.setWindowIcon(self.icon)

        # layout设置
        self.left_layout = QVBoxLayout()
        self.mid_layout = QVBoxLayout()
        self.right_layout = QFormLayout()
        # 布局设置
        self.left_box = QWidget()
        self.mid_box = QWidget()
        self.right_box = QWidget()
        self.left_box.setLayout(self.left_layout)
        self.mid_box.setLayout(self.mid_layout)
        self.right_box.setLayout(self.right_layout)
        # 设备初始化
        self.timerCamera = QTimer(self)
        self.timerCamera.timeout.connect(self.show_pic)
        self.timerCamera.start(10)
        self.sensor = Sensor.Sensor()
        data = self.sensor.getDatabySerial(3)
        # self.sensor.MQTTServer('123.56.0.232', 61613, 'Win10')
        # 组件初始化
        data = {'temp': '22',
                'hum': '64',
                'PPM': '65'}

        self.temp_area = QLineEdit()
        self.hum_area = QLineEdit()
        self.PPM_area = QLineEdit()
        self.temp_area.setText('温度：' + data['temp'] + '℃')
        self.hum_area.setText('湿度：' + data['hum'] + '%')
        self.PPM_area.setText('空气质量：' + data['PPM'])
        self.temp_area.setReadOnly(True)
        self.hum_area.setReadOnly(True)
        self.PPM_area.setReadOnly(True)
        self.cameraWidget = QLabel()
        self.therimgWidget = QLabel()
        self.show_pic()
        # cameraWidget2.newFrame.connect(self.onNewFrame)
        Pushbutton_start = QPushButton('start', self)
        # Pushbutton_start.clicked().connect(self.cameraDevice.paused)
        ComboBox_left = QComboBox()
        ComboBox_right = QComboBox()
        for i in range(0, 3):
            ComboBox_left.addItem('摄像头' + str(i + 1))  # unicode('摄像头' + str(i), 'utf-8')
            ComboBox_right.addItem('热成像' + str(i + 1))
        ComboBox_left.currentIndexChanged.connect(self.ChangeCamera)  # 发射currentIndexChanged信号，连接下面的selectionchange槽

        # 设置窗体
        hbox = QHBoxLayout()
        hbox.addWidget(self.left_box)
        hbox.addWidget(self.mid_box)
        hbox.addWidget(self.right_box)
        self.left_layout.addWidget(self.cameraWidget)
        self.left_layout.addWidget(ComboBox_left)
        self.mid_layout.addWidget(self.therimgWidget)
        self.mid_layout.addWidget(ComboBox_right)
        self.right_layout.addWidget(Pushbutton_start)
        self.right_layout.addWidget(self.temp_area)
        self.right_layout.addWidget(self.hum_area)
        self.right_layout.addWidget(self.PPM_area)
        self.setLayout(hbox)

        # 设置Title
        self.setWindowTitle('监控管理系统')  # unicode('监控管理系统', 'utf-8')
        self.setWindowIcon(self.icon)
        self.show()

    def MQTTWork(self):
        # print("开始多线程")

        self.wt = WorkThread()
        # 开始执行run()函数里的内容
        self.wt.start()

        # # 收到信号
        self.wt.sinOut.connect(self.net_back)  # 将信号连接至net_back函数

    def net_back(self, data):
        print(data)

    def show_pic(self):

        success_cam, frame_cam = self.aip.detectFaces()
        success_ther, frame_ther = self.thermal.getImage()

        if success_cam and success_ther:
            show_cam = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)
            show_ther = cv2.cvtColor(frame_ther, cv2.COLOR_BGR2RGB)

            showImage_cam = QImage(show_cam.data, show_cam.shape[1], show_cam.shape[0], QImage.Format_RGB888)
            showImage_ther = QImage(show_ther.data, show_ther.shape[1], show_ther.shape[0], QImage.Format_RGB888)

            self.cameraWidget.setPixmap(QPixmap.fromImage(showImage_cam))
            self.therimgWidget.setPixmap(QPixmap.fromImage(showImage_ther))

            self.timerCamera.start(10)

    def ChangeCamera(self, i):
        self.cameraDevice = cv2.VideoCapture(i)
        return


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # 启动界面
    splash = QSplashScreen(QPixmap("./imgs/loading.png"))
    splash.show()
    splash.showMessage(u"正在加载软件", alignment=Qt.AlignBottom)
    time.sleep(2)

    window = MyGUI()
    splash.finish(window)
    sys.exit(app.exec_())
