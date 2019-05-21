'''
Created on 2019年3月7日

@author: Administrator
'''
import cv2

class Camera():
    '''
    classdocs
    '''
    cam = 0

    def __init__(self, cameraid = 0):
        self.cam = cv2.VideoCapture(cameraid)
        
    def getImage(self):

        success, frame=self.cam.read()

        if success:

            show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return show
    
    def ChangeCamera(self,i):
        self.came = cv2.VideoCapture(i)