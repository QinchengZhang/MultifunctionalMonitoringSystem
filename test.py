# -*- coding: utf-8 -*
import json
import time

import cv2
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MMSTools import CameraDevice
from MMSTools import Thermal


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

    def __init__(self, parent=None):
        super(MyGUI, self).__init__(parent)
        self.CameraDevices = {}
        self.data = {}
        self.aip_config = {}
        self.thermal_com = 0
        self.MQTT_config = {}
        self.bwThread = WorkThread()
        self.initSettings()
        try:
            self.thermal = Thermal.Thermal(self.thermal_com)
        except:
            QMessageBox.warning(self, "提示", "热成像模块打开失败！", QMessageBox.Yes, QMessageBox.Yes)
            sys.exit()
        try:
            self.aip = CameraDevice.FacesOps(self.aip_config['APP_ID'], self.aip_config['APP_KEY'],
                                             self.aip_config['SECRET_KEY'], self.CameraDevices['Camera1']['name'])
        except:
            QMessageBox.warning(self, "提示", "摄像头打开失败！", QMessageBox.Yes, QMessageBox.Yes)
            sys.exit()
        super(MyGUI, self).__init__()
        self.initUI()

    def MQTTConnect(self, clientid, hostname, port, subscribe):
        global client, sub
        sub = subscribe
        client = mqtt.Client(client_id=clientid)
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        try:
            client.connect(hostname, port, keepalive=60)  # 向服务器发起连接
            self.bwThread = WorkThread()
            self.bwThread.updated.connect(self.show_env_from_server)
            self.bwThread.start()
        except Exception as e:
            QMessageBox.warning(self, "提示", "连接失败！", QMessageBox.Yes, QMessageBox.Yes)
            sys.exit()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(sub)

    def on_message(self, client, userdata, msg):
        self.data = json.loads(msg.payload)
        self.bwThread.updated.emit()  # 发送信号

    def show_env_from_server(self):
        self.temp_area.setValue(self.data['temp'])
        self.hum_area.setValue(self.data['hum'])
        self.PPM_area.setValue(self.data['PPM'])

    def initSettings(self):
        settings = open('settings.json', encoding='utf-8')
        settings = settings.read()
        settings = json.loads(settings)
        self.CameraDevices = settings['Cameras']
        self.aip_config = settings['Aip']
        self.thermal_com = settings['Thermal']['serial']
        self.MQTT_config = settings['MQTT']

    def initUI(self):
        self.MQTTConnect(clientid='MMS', hostname=self.MQTT_config['hostname'], port=self.MQTT_config['port'],
                         subscribe=self.MQTT_config['subscribe'])
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
        self.temp_area = QProgressBar(self)
        self.temp_area.setRange(0, 50)
        self.temp_area.setMinimumWidth(200)
        self.temp_area.setMinimumHeight(25)
        self.temp_area.setFormat('%v℃')
        self.hum_area = QProgressBar(self)
        self.hum_area.setMinimumWidth(200)
        self.hum_area.setMinimumHeight(25)
        self.PPM_area = QProgressBar(self)
        self.PPM_area.setMinimumWidth(200)
        self.PPM_area.setMinimumHeight(25)
        self.cameraWidget = QLabel()
        self.therimgWidget = QLabel()
        # self.show_env()
        self.show_pic()
        # Pushbutton_refresh = QPushButton('刷新数据', self)
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
        # self.right_layout.addWidget(Pushbutton_refresh)
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
        name = self.CameraDevices['Camera{:d}'.format(i + 1)]['name']
        self.aip.changeCam(name)
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
