# -*- coding: utf-8 -*-
import base64 as bs
import config
import cv2 as cv
import numpy as np
import math

# 初始化AipFace对象
aipFace = config.getAipFace()

# 读取图片
video = cv.VideoCapture(0)

# 设置
options = {
    'max_face_num': 10,  # 检测人脸的最大数量
}
imageType = "BASE64"


while True:
    _, frame = video.read()
    cv.imwrite('./temp/temp.png', frame)

    img = open('./temp/temp.png', 'rb')
    img = bs.b64encode(img.read())
    image64 = str(img, 'utf-8')
    # print(str(img))
    result = aipFace.detect(image64, imageType, options)
    if result['error_code'] == 0:
        face_list = result['result']['face_list']
        for face in face_list:
            print(face)
            location = face['location']
            # print(location)
            point = np.empty([4, 2], dtype=int)
            point[0][0] = int(location['left'])
            point[0][1] = int(location['top'])
            point[1][0] = int(location['left'] + location['width'] * math.cos(math.radians(location['rotation'])))
            point[1][1] = int(location['top'] + location['width'] * math.sin(math.radians(location['rotation'])))
            point[2][0] = int(location['left'] - location['height'] * math.sin(math.radians(location['rotation'])))
            point[2][1] = int(location['top'] + location['height'] * math.cos(math.radians(location['rotation'])))
            point[3][0] = int(point[2][0] + location['width'] * math.cos(math.radians(location['rotation'])))
            point[3][1] = int(point[2][1] + location['width'] * math.sin(math.radians(location['rotation'])))
            cv.line(frame, (point[0][0], point[0][1]), (point[1][0], point[1][1]), (0, 0, 255), 2)
            cv.line(frame, (point[0][0], point[0][1]), (point[2][0], point[2][1]), (0, 0, 255), 2)
            cv.line(frame, (point[2][0], point[2][1]), (point[3][0], point[3][1]), (0, 0, 255), 2)
            cv.line(frame, (point[1][0], point[1][1]), (point[3][0], point[3][1]), (0, 0, 255), 2)
            '''cv.rectangle(frame, (int(location['left']), int(location['top'])),
                     (int(location['width'] + location['left']), int(location['height'] + location['top'])),
                     (0, 0, 255), 2)  # opencv的标框函数'''
        # cv.imwrite('./temp/temp.png', frame)
        # cv.cvtColor(frame, cv.COLOR_BGR2RGB,frame)
        cv.namedWindow("video")
        cv.imshow('video', frame)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
cv.destroyAllWindows()
