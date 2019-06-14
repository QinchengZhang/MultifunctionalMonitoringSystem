import cv2 as cv
import time

cam = cv.VideoCapture('rtsp://admin:123456@192.168.137.155:554/stream1')
print(cam.isOpened())
while True:
    _, frame = cam.read()
    cv.imshow('frame', frame)
    filename = './imgs/faces/{}.jpg'.format(int(time.time()))
    print(filename)
    print(cv.imwrite(filename, frame))
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()
