# -*- coding: utf-8 -*-
import base64 as bs
import config
import cv2 as cv

# 初始化AipFace对象
aipFace = config.getAipFace()

# 读取图片
video = cv.VideoCapture(0)

# 设置
options = {
    'max_face_num': 10,  # 检测人脸的最大数量
}
group_id_list = "cdmcadmin,cdmcuser,cdmcstranger"
imageType = "BASE64"


while True:
    _, frame = video.read()
    cv.imwrite('./temp/temp.png', frame)

    img = open('./temp/temp.png', 'rb')
    img = bs.b64encode(img.read())
    image64 = str(img, 'utf-8')
    # print(str(img))
    search = aipFace.search(image64, imageType, group_id_list)
    result = aipFace.detect(image64, imageType, options)
    if result['error_code'] == 0 and search['error_code'] == 0:
        print(result)
        face_list = result['result']['face_list']
        for face in face_list:

            location = face['location']
            # print(location)
            cv.rectangle(frame, (int(location['left']), int(location['top'])),
                     (int(location['width'] + location['left']), int(location['height'] + location['top'])),
                     (0, 0, 255), 2)  # opencv的标框函数
        # cv.imwrite('./temp/temp.png', frame)
        # cv.cvtColor(frame, cv.COLOR_BGR2RGB,frame)
        cv.namedWindow("video")
        cv.imshow('video', frame)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
cv.destroyAllWindows()
