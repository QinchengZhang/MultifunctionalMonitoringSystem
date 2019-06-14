# -*- coding: utf-8 -*
import time
import json
import cv2
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MMSTools import Sensor
from MMSTools import CameraDevice
from MMSTools import Thermal
from MMSTools import EnvServer


class WorkThread(QThread):
    updated = pyqtSignal()  # 自定义信号，更新数据

    def __init__(self, parent=None):
        super(WorkThread, self).__init__(parent)
        self.flag = 1

    def run(self):
        while True:
            if self.flag == 1:
                client.loop(timeout=60)
            else:
                break

    def stop(self):
        self.flag = 0
        print(self.flag)


class MyGUI(QtWidgets.QWidget):
    CameraDevices = 0
    menubar = 0
    icon = 0
    left_layout = 0
    mid_layout = 0
    right_layout = 0
    left_box = 0
    mid_box = 0
    right_box = 0
    timerSensor = 0
    timerCamera = 0
    cameraWidget = 0
    therimgWidget = 0
    temp_area = 0
    hum_area = 0
    PPM_area = 0

    def __init__(self):
        self.data = {}
        self.bwThread = WorkThread()

        self.initCameras()
        self.thermal_com = 'COM3'
        self.sensor_com = 'COM4'
        self.thermal = Thermal.Thermal(self.thermal_com)
        self.aip = CameraDevice.FacesOps(self.CameraDevices['Camera1']['name'])
        super(MyGUI, self).__init__()
        self.initUI()

    def MQTTConnect(self, clientid, hostname):
        global client
        client = mqtt.Client(client_id=clientid)
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        try:
            client.connect(hostname, 18830, keepalive=60)  # 向服务器发起连接
            self.bwThread = WorkThread()
            self.bwThread.updated.connect(self.show_env_from_server)
            self.bwThread.start()
        except Exception as e:
            QMessageBox.information(self, self.tr("提示"), self.tr("连接失败！"))

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe('MMS/devices/environment/')

    def on_message(self, client, userdata, msg):
        self.data = json.loads(msg.payload)
        self.bwThread.updated.emit()  # 发送信号

    def show_env_from_server(self):
        self.temp_area.setText('%.2f℃' % self.data['temp'])
        self.hum_area.setText('%.2f' % self.data['hum'] + '%')
        self.PPM_area.setText('%d' % self.data['PPM'])

    def initCameras(self):
        cameras = open('Cameras.json', encoding='utf-8')
        cameras = cameras.read()
        self.CameraDevices = json.loads(cameras)

    def initUI(self):
        self.MQTTConnect(clientid='MMS', hostname='mq.tongxinmao.com')
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
        # 组件初始化
        temp_label = QLabel('温度')
        hum_label = QLabel('湿度')
        PPM_label = QLabel('PPM')
        self.temp_area = QLineEdit()
        self.hum_area = QLineEdit()
        self.PPM_area = QLineEdit()
        self.temp_area.setReadOnly(True)
        self.hum_area.setReadOnly(True)
        self.PPM_area.setReadOnly(True)
        self.cameraWidget = QLabel()
        self.therimgWidget = QLabel()
        # self.show_env()
        self.show_pic()
        Pushbutton_refresh = QPushButton('刷新数据', self)
        ComboBox_left = QComboBox()
        for key, values in self.CameraDevices.items():
            ComboBox_left.addItem('摄像头{:d}:{location}'.format(values['ID'], location=values['location']))
        ComboBox_left.currentIndexChanged.connect(self.ChangeCamera)  # 发射currentIndexChanged信号，连接下面的selectionchange槽

        # 设置窗体
        hbox = QHBoxLayout()
        hbox.addWidget(self.left_box)
        hbox.addWidget(self.mid_box)
        hbox.addWidget(self.right_box)
        self.left_layout.addWidget(self.cameraWidget)
        self.left_layout.addWidget(ComboBox_left)
        self.mid_layout.addWidget(self.therimgWidget)
        self.right_layout.addWidget(Pushbutton_refresh)
        self.right_layout.addWidget(temp_label)
        self.right_layout.addWidget(self.temp_area)
        self.right_layout.addWidget(hum_label)
        self.right_layout.addWidget(self.hum_area)
        self.right_layout.addWidget(PPM_label)
        self.right_layout.addWidget(self.PPM_area)
        self.setLayout(hbox)

        # 设置Title
        self.setWindowTitle('监控管理系统')  # unicode('监控管理系统', 'utf-8')
        self.setWindowIcon(self.icon)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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

            self.timerCamera.start(100)

    def ChangeCamera(self, i):
        print(i)
        self.aip.changeCam(self.CameraDevices[i]['name'])
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
