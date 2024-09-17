import cv2 as cv
import imutils


def road(hsv, low, high, err, img):
    rd = cv.GaussianBlur(hsv, (11, 11), 0)
    rd = cv.inRange(rd, low, high)
    imgCenter = img.shape[1] // 2
    cv.imshow("roadModified", rd)
    cnt, _ = cv.findContours(rd, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    rx = 0
    area = 0
    maxArea = 0
    R = None
    for c in cnt:
        M = cv.moments(c)
        if M["m00"] != 0:
            RCx = int(M["m10"] / M["m00"])
            area = cv.contourArea(c)
            if area > maxArea:  #abs(RCx - 100) < closer:  # and w*h>3500:
                #closer = abs(RCx - 100)
                maxArea = area
                rx = RCx
                R = c
    if R is not None:
        cv.drawContours(img, [R], -1, (120, 255, 0), 2)
        cv.circle(img, (rx, 25), 40, (255, 0, 0), 2)
        area = cv.contourArea(R)
        err=0
    else:
        #recalculate min and max
        print("road not found!")
        err =1
    return rx-imgCenter, err


def features(tag, low, high, img, hsv):
    filtro = cv.inRange(hsv, low, high)
    filtro = cv.dilate(filtro, (15, 15), iterations=3)
    closer = 50000
    cnts = cv.findContours(filtro, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    closerCoordinates = None
    for c in cnts:
        cY = 0
        cX = 0
        M = cv.moments(c)
        imgCenter = img.shape[1] // 2
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #cv.drawContours(recorte, [c], -1, (0, 255, 0), 2)
        if abs(cX - imgCenter) <= abs(closer):
            closer = cX - imgCenter
            cv.circle(img, (cX, cY), 7, (255, 255, 255), -1)
            cv.putText(img, tag, (cX - 20, cY - 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return closer, img
