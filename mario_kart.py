import cv2 as cv
import os
import numpy as np
import keyboard
import imutils
import mss
import adjust_screen

dale = False
#392 145 392 293
threshold = 25
err = 0


def getRoadColor(fr):
    #maybe in the future i wil add adaptive road detection
    cy = int(fr.shape[0] / 2)
    cx = int(fr.shape[1] / 2)
    delta = 50
    img = fr[cy - 15:cy + 15, cx - 15:cx + 15]
    #use color of biggest contour
    #img=cv.GaussianBlur(img,(51,51),0)
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    vals = [0, 0, 0]
    for i in range(3):
        vals[i] = np.average(img[:, :, i]) - delta
    low = np.array(vals)
    for i in range(3):
        vals[i] = np.average(img[:, :, i]) + delta
        #vals[i]=np.max(img[:,:,i])+delta
    high = np.array(vals)
    cv.imshow("Ncolor", img)
    print("new road color calibration calculated")
    return low, high


def detectRoad(hsv, low, high, err):
    rd = cv.GaussianBlur(hsv, (11, 11), 0)
    rd = cv.inRange(rd, low, high)
    cv.imshow("roadModified",rd)
    cnt, _ = cv.findContours(rd, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    rx = 0
    area=0
    maxArea=0
    R = None
    for c in cnt:
        M = cv.moments(c)
        if M["m00"] != 0:
            RCx = int(M["m10"] / M["m00"])
            area = cv.contourArea(c)
            if area>maxArea:#abs(RCx - 100) < closer:  # and w*h>3500:
                #closer = abs(RCx - 100)
                maxArea = area
                rx = RCx
                R = c
    if R is not None:
        cv.drawContours(roadView, [R], -1, (120, 255, 0), 2)
        cv.circle(roadView, (rx, 25), 40, (255, 0, 0), 2)
        area = cv.contourArea(R)
    else:
        #recalculate min and max
        print("road not found!")
        err += 1
    if area < 100:
        err += 1
    if area / (hsv.shape[0] * hsv.shape[1]) > .8:
        err += 1
    return rx, err


def detectFeatures(str, low, high, img, hsv):
    filtro = cv.inRange(hsv, low, high)
    filtro = cv.dilate(filtro, (15, 15), iterations=3)
    closer = 50000
    cnts = cv.findContours(filtro, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for c in cnts:
        cY = 0
        cX = 0
        M = cv.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #cv.drawContours(recorte, [c], -1, (0, 255, 0), 2)
        if abs(cX - cx) <= abs(closer):
            closer = cX - cx
            cv.circle(img, (cX, cY), 7, (255, 255, 255), -1)
            cv.putText(img, str, (cX - 20, cY - 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return closer, img


low = np.array([0, 0, 63])
high = np.array([38, 53, 124])
tLow = np.array([53, 173, 108])
tHigh = np.array([56, 202, 255])
iLow = np.array([58, 205, 241])
iHigh = np.array([162, 255, 255])
vHigh = np.array([0, 255, 195])
vLow = np.array([0, 255, 195])

## check if setup has been run
if os.path.isfile("config"):
    f = open("config", "r")
    t = int(f.readline())
    l = int(f.readline())
    w = int(f.readline())
    h = int(f.readline())
    f.close()
    print("config loaded")
else:
    t, l, w, h = adjust_screen.getValues()
    f = open("config", "w")
    f.write(str(t) + "\n")
    f.write(str(l) + "\n")
    f.write(str(w) + "\n")
    f.write(str(h) + "\n")
    f.close()
    print("config saved")

with mss.mss() as sct:
    while True:
        monitor = {"top": l, "left": t, "width": w, "height": h}
        frame = np.array(sct.grab(monitor))

        if keyboard.is_pressed('h'):
            dale = True

        if keyboard.is_pressed('g'):
            dale = False

        keys = 'l'

        cy = int((monitor["height"]) / 2)
        cx = int((monitor["width"]) / 2)
        roadView = frame[int(h*.2):int(h*.35),  int(w*.3):int(w*.7)]
        hsv = cv.cvtColor(roadView, cv.COLOR_BGR2HSV)
        playerView = frame[int(h*.3):int(h*.4), int(w*.4):int(w*.6)]
        fhsv = cv.cvtColor(playerFront, cv.COLOR_BGR2HSV)

        #road detection
        roadX, err = detectRoad(hsv, low, high, err)
        cv.imshow("playerFront", playerFront)
        #print(rx)
        #if the road is not found for 5 frames or j is pressed it recalculates the road threshold
        #if (err > 7) or keyboard.is_pressed('j'):
        #    err = 0
        #    #recalc
        #    low, high = getRoadColor(playerFront)

        icloser, playerFront = detectFeatures("itembox", iLow, iHigh, playerFront, fhsv)  #get closest itembox
        tcloser, playerFront = detectFeatures("tubo", tLow, tHigh, playerFront, fhsv)  #get closest tube

        turning = False

        #vuelta
        roadDelta = roadX - cx
        #print(tcloser,icloser,treshold)
        ## all of this should be commented out
        road = abs(roadDelta) > threshold
        tubo = abs(tcloser) < 10
        box = abs(icloser) < 5
        if road or tubo or box:
            if tubo:
                road = 1

            if roadDelta * road < 0 or icloser * box < 0 or roadDelta * turning < 0:
                keyboard.release('q')
                keyboard.release('d')
                if len(keys) != 0:
                    keys += '+'
                keys += 'a'

            if roadDelta * road > 0 or icloser * box > 0 or roadDelta * turning > 0:
                keyboard.release('q')
                keyboard.release('a')
                if len(keys) != 0:
                    keys += '+'
                keys += 'd'

            if road:
                threshold = abs(roadDelta) - 1 ## que onda con esto

        else:
            if threshold > 10:
                threshold -= 1
            if len(keys) != 0:
                keys += '+'
            keys += 'q'
            keyboard.release('a')
            keyboard.release('d')

        cv.imshow('contours', frame)
        cv.imshow('roadView', roadView)

        keyboard.release('p')

        if len(keys) != 0 and dale:
            keyboard.send(keys, True, False)

        if cv.waitKey(20) == 27:
            break

cv.destroyAllWindows()
keyboard.release('x')