import cv2 as cv
import numpy as np
#import pyautogui
import keyboard
import imutils
import mss
dale = False
#392 145 392 293
treshold=25
count=0

#fourcc = cv.VideoWriter_fourcc('m','p','4','v')

#writer= cv.VideoWriter('marioKart.avi', -1, 20, (1366,768))
drifting=False
with mss.mss() as sct:
    while "Screen capturing":
        monitor = {"top":391, "left":119, "width": 444, "height":332}
        img = np.array(sct.grab(monitor))   
        screen = np.array(sct.grab({"top":0, "left":0, "width": 1366, "height":768}))
        screen = cv.resize(screen,(1366,768))
        #writer.write(screen)
        keys = ''
        if keyboard.is_pressed('h'):
            dale = True

        if keyboard.is_pressed('g'):
            dale = False

        keys = 'p'

        #im1 = pyautogui.screenshot()
        #img = np.array(im1)
        frame = img
        #frame = frame[403:702, 142:540]
        wo2 = 100
        ho2 = 100
        cy = int((monitor["height"])/2)
        cx = int((monitor["width"])/2)
        
        recorte = frame[cy-ho2:cy-int(ho2/2), cx-wo2:cx+wo2]
        hsv = cv.cvtColor(recorte, cv.COLOR_BGR2HSV)

        low = np.array([0, 0, 63])
        high = np.array([38, 53, 124])
        tLow = np.array([53, 173, 108])
        tHigh = np.array([56, 202, 255])
        iLow = np.array([58, 205, 241])
        iHigh = np.array([162, 255, 255])
        vHigh= np.array([0,255,195])
        vLow= np.array([0,255,195])

        frecorte = frame[cy-50:cy-5, cx-wo2:cx+wo2]
        fhsv = cv.cvtColor(frecorte, cv.COLOR_BGR2HSV)
        vfiltro=cv.inRange(hsv,vLow,vHigh)
        ifiltro = cv.inRange(fhsv, iLow, iHigh)
        tfiltro = cv.inRange(fhsvfhsv, tLow, tHigh)
        filtro = cv.inRange(hsv, low, high)

        cv.imshow('itemBox', ifiltro)
        cv.imshow('tuberias', tfiltro)
        cv.imshow('vuelta',vfiltro)
        #centro del camino
        rx = 0
        object = cv.moments(filtro)
        if object['m00'] > 5000:
            rx = int(object['m10']/object['m00'])
            cy = int(object['m01']/object['m00'])
            cv.circle(recorte, (rx, cy), 40, (255, 0, 0), 2)

        countours, _ =cv.findContours(tfiltro, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
        for cnt in countours:
            #area=cv.contourArea(cnt)
            #if area < 50:
            approx= cv.approxPolyDP(cnt,0.012*cv.arcLength(cnt,True),True)
            cv.drawContours(recorte, [approx],0,(0,255,0),2)

        

        ifiltro = cv.dilate(ifiltro, (15,15), iterations=3)

        icloser = 50000
        cnts = cv.findContours(ifiltro, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            M = cv.moments(c)
            if  M["m00"] !=0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            #cv.drawContours(frecorte, [c], -1, (0, 255, 0), 2)
            if abs(cX-wo2) <= abs(icloser):
                icloser= cX-wo2
                cv.circle(frecorte, (cX, cY), 7, (255, 255, 255), -1)
                cv.putText(frecorte, "itembox", (cX - 20, cY - 20),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
        tfiltro = cv.dilate(tfiltro, (15,15), iterations=3)
        cv.imshow('frecorte',frecorte)
        tcloser =50000
        cnts = cv.findContours(tfiltro, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
            cY=0 
            cX=0
            M = cv.moments(c)
            if  M["m00"] !=0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            #cv.drawContours(recorte, [c], -1, (0, 255, 0), 2)
            if abs(cX-wo2) <= abs(tcloser):
                tcloser=cX-wo2
                cv.circle(frecorte, (cX, cY), 7, (255, 255, 255), -1)
                cv.putText(frecorte, "tubo", (cX - 20, cY - 20),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    

        cnts = cv.findContours(vfiltro, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        vuelta=False
        #for c in cnts:
        #    cY=0 
        #    cX=0
        #    M = cv.moments(c)
        #    cv.drawContours(recorte, [c], -1, (255, 0, 0), 2)
        #    if  M["m00"] !=0:
        #        cX = int(M["m10"] / M["m00"])
        #        cY = int(M["m01"] / M["m00"])
        #    vuelta = True
        object = cv.moments(vfiltro)
        vx=0
        if object['m00'] > 5000:
            vx = int(object['m10']/object['m00'])
            cy = int(object['m01']/object['m00'])
            cv.circle(recorte, (vx, cy), 40, (255, 0, 0), 2)
            vuelta=True
        diferenciaV=vx-wo2


        #cv.line(frecorte,(tcloser+wo2,0),(tcloser+wo2,50),(255,0,0),5,1)
        #print(tcloser, icloser)



        #vuelta
        diferenciaR = rx-wo2
        #print(tcloser,icloser,treshold)
        if drifting: 
            treshold-=3
        road=abs(diferenciaR) > treshold
        tubo= abs(tcloser)<10
        box=abs(icloser)<5
        #print(road,tubo,box)
        if road or  tubo or box:
            print(diferenciaR)
            #if abs(diferenciaR*road) > 20 and abs(diferenciaR*road) < 30 :
            #    if len(keys) != 0:
            #        keys += '+'
            #    keys += 'w'
            #else:
            #    keyboard.release('w')

            if tubo:
                road=1

            #if vuelta: 
                #road=True

            if diferenciaR*road < 0 or icloser*box<0 or diferenciaV*vuelta<0:
                keyboard.release('q')
                keyboard.release('d')
                if len(keys) != 0:
                    keys += '+'
                keys += 'a'
                

            if diferenciaR*road > 0  or icloser*box>0 or diferenciaV*vuelta>0:
                keyboard.release('q')
                keyboard.release('a')
                if len(keys) != 0:
                    keys += '+'
                keys += 'd'
            
            if drifting:
                count+=1
                if count %2:
                    keyboard.release('a')
                    keyboard.press('d')
                else:
                    keyboard.release('d')
                    keyboard.press('a')

            
            if road :
                treshold=abs(diferenciaR)-1
            if vuelta and not drifting:
                drifting = True
                #print("drifting!")
                keyboard.press('e')
            if not vuelta:
                drifting=0
                keyboard.release('e')
        else:

            drifting=False
            keyboard.release('e')
            if treshold > 10:
                treshold-=1
            if len(keys) != 0:
                keys += '+'
            keys += 'q'
            keyboard.release('a')
            keyboard.release('d')

        cv.imshow('contours', frame)
        cv.imshow('recorte', recorte)

        keyboard.release('p')
        
        #cv.imshow('screen', screen)
        
        if len(keys) != 0 and dale:
            keyboard.send(keys, 1, 0)

        if cv.waitKey(20) == 27:
            break

cv.destroyAllWindows()
keyboard.release('x')
