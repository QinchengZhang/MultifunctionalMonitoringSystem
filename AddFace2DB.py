# -*- coding: utf-8 -*-
import base64 as bs
import config
import cv2 as cv
from MMSTools import CameraDevice

# 初始化AipFace对象
aipFace = CameraDevice.FacesOps('rtsp://admin:123456@192.168.137.155:554/stream1')

# 设置
options = {
    'action_type': 'APPEND',  # 当user_id在库中已经存在时，对此user_id重复注册时，新注册的图片默认会追加到该user_id下
}

while True:
    result, success, frame = aipFace.reg2DB('cdmcadmin', 'zqc', options=options)
    print(result)
    cv.imshow('regface', frame)
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()
