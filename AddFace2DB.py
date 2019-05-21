# -*- coding: utf-8 -*-
import base64 as bs
import config
import cv2 as cv

# 初始化AipFace对象
aipFace = config.getAipFace()

video = cv.VideoCapture(0)

# 设置
options = {
    'user_info': 'shz',  # 用户信息，身份标识等
    'action_type': 'APPEND',  # 当user_id在库中已经存在时，对此user_id重复注册时，新注册的图片默认会追加到该user_id下
}
imageType = "BASE64"

_, frame = video.read()
cv.imwrite('./temp/temp.png', frame)
img = open('./temp/temp.png', 'rb')
img = bs.b64encode(img.read())
image64 = str(img, 'utf-8')
result = aipFace.addUser(image64, imageType, group_id='cdmcuser', user_id='001', options=options)  # group_id为数据库中用户组名，user_id为要新建的用户id
print(result)
