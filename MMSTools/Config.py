# -*- coding: utf-8 -*-
from aip import AipFace

# 定义常量
APP_ID = '14703084'
API_KEY = 'HGhYDodrGbB9SQleM1l1XRiG'
SECRET_KEY = 'V6dKuN6VnLXdhEuvGgIFWVNSsD2lL1Ho'



def getAipFace():
    # 初始化AipFace对象
    return AipFace(APP_ID, API_KEY, SECRET_KEY)
