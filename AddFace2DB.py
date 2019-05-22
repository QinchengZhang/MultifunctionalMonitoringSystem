# -*- coding: utf-8 -*-
import base64 as bs
import config
import cv2 as cv
from MMSTools import CameraDevice

# 初始化AipFace对象
aipFace = CameraDevice.FacesOps()

# 设置
options = {
    'action_type': 'APPEND',  # 当user_id在库中已经存在时，对此user_id重复注册时，新注册的图片默认会追加到该user_id下
}

while True:
    result, success, frame = aipFace.reg2DB('cdmcadmin', 'zqc', options=options)
    cv.imshow('regface', frame)
    print(result)
