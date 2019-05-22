# -*- coding: utf-8 -*-
import base64 as bs
import time

import cv2 as cv
import math
import numpy as np
from MMSTools import Config


class FacesOps(object):
    def __init__(self, cam=0):
        self.aip = Config.getAipFace()
        self.video = cv.VideoCapture(cam)
        if not self.video.isOpened():
            print('无效摄像头')
            self.video = cv.VideoCapture(0)
        self.video.set(cv.CAP_PROP_FPS, 90)

    def image_to_base64(self, image_np):

        image = cv.imencode('.jpg', image_np)[1]
        image_code = str(bs.b64encode(image))[2:-1]

        return image_code

    def base64_to_image(self, base64_code):

        # base64解码
        img_data = bs.b64decode(base64_code)
        # 转换为np数组
        img_array = np.fromstring(img_data, np.uint8)
        # 转换成opencv可用格式
        img = cv.imdecode(img_array, cv.COLOR_RGB2BGR)

        return img

    def detectFaces(self):
        # 设置
        detect_options = {
            'max_face_num': 10,  # 检测人脸的最大数量
        }
        group_id_list = "cdmcadmin,cdmcuser,cdmcstranger"
        search_options = {
            'max_user_num': 1,
        }
        imageType = "BASE64"

        success, frame = self.video.read()
        image64 = self.image_to_base64(frame)
        result = self.aip.detect(image64, imageType, detect_options)
        if result['error_code'] == 0:
            if result['result']['face_num'] > 0:
                face_list = result['result']['face_list']
                for face in face_list:
                    location = face['location']
                    point = np.empty([4, 2], dtype=int)
                    point[0][0] = int(location['left'])
                    point[0][1] = int(location['top'])
                    point[1][0] = int(
                        location['left'] + location['width'] * math.cos(math.radians(location['rotation'])))
                    point[1][1] = int(
                        location['top'] + location['width'] * math.sin(math.radians(location['rotation'])))
                    point[2][0] = int(
                        location['left'] - location['height'] * math.sin(math.radians(location['rotation'])))
                    point[2][1] = int(
                        location['top'] + location['height'] * math.cos(math.radians(location['rotation'])))
                    point[3][0] = int(point[2][0] + location['width'] * math.cos(math.radians(location['rotation'])))
                    point[3][1] = int(point[2][1] + location['width'] * math.sin(math.radians(location['rotation'])))
                    min_pos = np.amin(point, 0)
                    max_pos = np.amax(point, 0)
                    facearea = frame[min_pos[1]:max_pos[1], min_pos[0]:max_pos[0]]
                    image64 = self.image_to_base64(facearea)
                    search = self.aip.search(image64, imageType, group_id_list, search_options)
                    if search['error_code'] == 0:
                        user = search['result']['user_list'][0]
                        if int(user['score']) >= 70:
                            if user['group_id'] == 'cdmcadmin' or user['group_id'] == 'cdmcuser':
                                font = cv.FONT_HERSHEY_SIMPLEX  # 定义字体
                                label = 'admin' if user['group_id'] == 'cdmcadmin' else 'user'
                                cv.putText(frame, label + ':' + user['user_info'], (min_pos[0], min_pos[1]), font, 0.9,
                                           (255, 255, 255), 1)
                                # 图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
                            else:
                                add_user_options = {
                                    'action_type': 'APPEND',  # 当user_id在库中已经存在时，对此user_id重复注册时，新注册的图片默认会追加到该user_id下
                                }
                                timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                                result = self.aip.addUser(image64, imageType, group_id='cdmcstranger',
                                                          user_id=user['user_id'],
                                                          options=add_user_options)
                                # self.reg2DB(image64, group_id='cdmcstranger', user_id='stranger' + str(datetime.date))
                                font = cv.FONT_HERSHEY_SIMPLEX  # 定义字体
                                cv.putText(frame, 'stranger', (min_pos[0], min_pos[1]), font, 0.9,
                                           (255, 255, 255), 1)
                        else:
                            add_user_options = {
                                'action_type': 'APPEND',  # 当user_id在库中已经存在时，对此user_id重复注册时，新注册的图片默认会追加到该user_id下
                            }
                            timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                            result = self.aip.addUser(image64, imageType, group_id='cdmcstranger',
                                                      user_id='stranger' + timestamp,
                                                      options=add_user_options)
                            # self.reg2DB(image64, group_id='cdmcstranger', user_id='stranger' + str(datetime.date))
                            font = cv.FONT_HERSHEY_SIMPLEX  # 定义字体
                            cv.putText(frame, 'stranger', (min_pos[0], min_pos[1]), font, 0.9,
                                       (255, 255, 255), 1)
                    cv.line(frame, (point[0][0], point[0][1]), (point[1][0], point[1][1]), (0, 0, 255), 2)
                    cv.line(frame, (point[0][0], point[0][1]), (point[2][0], point[2][1]), (0, 0, 255), 2)
                    cv.line(frame, (point[2][0], point[2][1]), (point[3][0], point[3][1]), (0, 0, 255), 2)
                    cv.line(frame, (point[1][0], point[1][1]), (point[3][0], point[3][1]), (0, 0, 255), 2)
        return success, frame

    def reg2DB(self, img, group_id, user_id, user_info=''):
        options = {
            'user_info': user_info,
        }
        result = self.aip.addUser(img, "BASE64", group_id=group_id, user_id=user_id,
                                  options=options)
        return result
