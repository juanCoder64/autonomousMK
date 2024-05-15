import cv2 as cv
import keyboard
import numpy as np
import mss

#def nothing (val):
##
def getValues():
    x=0
    y=0
    w=600
    h=100
    print("Adjust the capture area to lower screen, press f when done")
    print("Use WASD to move the screen")
    print("Use arrow keys to scale the screen")
    with mss.mss() as sct:
        while True:
            x=x+(keyboard.is_pressed("d"))
            x=x-(keyboard.is_pressed("a"))
            y=y-(keyboard.is_pressed("w"))
            y=y+(keyboard.is_pressed("s"))
            w=w-(keyboard.is_pressed("left"))
            w=w+(keyboard.is_pressed("right"))
            h=h-(keyboard.is_pressed("up"))
            h=h+(keyboard.is_pressed("down"))

            monitor = {'top': y, 'left': x, 'width': w, 'height': h}
            img = np.array(sct.grab(monitor))
            cv.imshow('screen', img)
            if cv.waitKey(1) == ord('f'):
                break
    cv.destroyAllWindows()
    return x,y,w,h

