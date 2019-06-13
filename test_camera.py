import cv2 as cv

cam = cv.VideoCapture('192.168.12.22:554')
print(cam.isOpened())
while True:
    _, frame = cam.read()
    cv.imshow('frame', frame)
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()