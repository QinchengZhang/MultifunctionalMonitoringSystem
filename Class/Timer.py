# -*- coding: utf-8 -*
'''
Created on 2019年2月28日

@author: Administrator
'''
from PyQt4 import QtCore
import time

class Timer(QtCore.QThread):

    def __init__(self, signal="updateTime()", parent=None):
        super(Timer, self).__init__(parent)
        self.stoped = False
        self.signal = signal
        self.mutex = QtCore.QMutex()

    def run(self):
        with QtCore.QMutexLocker(self.mutex):
            self.stoped = False
        while True:
            if self.stoped:
                return
            self.emit(QtCore.SIGNAL(self.signal))
            #40毫秒发送一次信号
            time.sleep(0.04)

    def stop(self):
        with QtCore.QMutexLocker(self.mutex):
            self.stoped = True

    def isStoped(self):
        with QtCore.QMutexLocker(self.mutex):
            return self.stoped