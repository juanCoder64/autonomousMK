import cv2 as cv
import numpy as np
import mss

def nothing (val):
    pass
cv.namedWindow('sliders')
cv.createTrackbar('x','sliders', 0, 1000,nothing) 
cv.createTrackbar('y','sliders', 0, 1000,nothing)
cv.createTrackbar('w','sliders', 100, 1000,nothing)
cv.createTrackbar('h','sliders', 100, 1000,nothing)
def getValues():
    print("Adjust the capture area to lower screen, press d when done")
    with mss.mss() as sct:
        while True:
            x = cv.getTrackbarPos('x', 'sliders')
            y = cv.getTrackbarPos('y', 'sliders')
            w = cv.getTrackbarPos('w', 'sliders')
            h = cv.getTrackbarPos('h', 'sliders')
            monitor = {'top': y, 'left': x, 'width': w, 'height': h}
            img = np.array(sct.grab(monitor))
            cv.imshow('screen', img)
            if cv.waitKey(1) == ord('d'):
                break
    cv.destroyAllWindows()
    return x,y,w,h

