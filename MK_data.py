from pickle import TRUE
import cv2 as cv
import numpy as np
import csv
#import pyautogui
import keyboard
import imutils
import mss
dale = False
#392 145 392 293
treshold=25
import joblib
sc = joblib.load('sc.joblib')
datos=[]
from keras.models import Sequential, save_model, load_model
import numpy as np
import array
model = load_model("./model", compile = True)
#fourcc = cv.VideoWriter_fourcc('m','p','4','v')
Dcap=False
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

        if keyboard.is_pressed('r'):
            Dcap = True

        if keyboard.is_pressed('g'):
            dale = False
            Dcap=False

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
        tLow = np.array([56, 143, 154])
        tHigh = np.array([58, 188, 240])
        iLow = np.array([112, 0, 152])
        iHigh = np.array([169, 255, 255])

        frecorte = frame[cy-50:cy-5, cx-wo2:cx+wo2]
        fhsv = cv.cvtColor(frecorte, cv.COLOR_BGR2HSV)
        ifiltro = cv.inRange(fhsv, iLow, iHigh)
        tfiltro = cv.inRange(fhsv, tLow, tHigh)
        filtro = cv.inRange(hsv, low, high)

        #cv.imshow('itemBox', ifiltro)
        #cv.imshow('tuberías', tfiltro)
        
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
            cv.drawContours(frame, [c], -1, (0, 255, 0), 2)
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
            cv.drawContours(frame, [c], -1, (0, 255, 0), 2)
            if abs(cX-wo2) <= abs(tcloser):
                tcloser=cX-wo2
                cv.circle(frecorte, (cX, cY), 7, (255, 255, 255), -1)
                cv.putText(frecorte, "tubo", (cX - 20, cY - 20),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    

        #cv.line(frecorte,(tcloser+wo2,0),(tcloser+wo2,50),(255,0,0),5,1)
        #print(tcloser, icloser)



        #vuelta
        diferenciaR = rx-wo2
        #print(tcloser,icloser,treshold)
        if drifting: 
            treshold-=3
        road=abs(diferenciaR) > treshold
        tubo= abs(tcloser)<8
        box=abs(icloser)<7
        if tcloser == -100: tcloser=0

        if Dcap:
            if diferenciaR != -100:
                print(diferenciaR,(tcloser!=50000)*tcloser,(icloser!=50000)*icloser,keyboard.is_pressed('a')+0,keyboard.is_pressed('d')+0)
                datos+=[[diferenciaR,(tcloser!=50000)*tcloser,(icloser!=50000)*icloser,keyboard.is_pressed('a')+0,keyboard.is_pressed('d')+0]]
            else:
                Dcap=False

        elif len(datos)>0:
            with open ('Ndata.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(datos)
            datos=[]
        
        
        if dale:
            use_samples = np.array([[diferenciaR/23.155,(tcloser!=50000)*tcloser, (icloser!=50000)*icloser]])
            transformData = sc.transform(use_samples)
            predictions = model(use_samples)
            
            p1=(predictions[0,1].numpy())
            p2=(predictions[0,0].numpy())
            

            #print(p1,p2,predictions[0,1].numpy(),predictions[0,0].numpy())
            keyboard.release('p')
            keyboard.press('p')

            if p2>0.9 or p1 >0.9:
                if(p1<p2):
                    keyboard.release('d')
                    print("a")
                    keyboard.press('a')
                else:
                    keyboard.release('a')
                    print("d")
                    keyboard.press('d')
            else:
                keyboard.release('a')
                keyboard.release('d')

        

        cv.imshow('contours', frame)
        cv.imshow('recorte', recorte)


        if cv.waitKey(20) == 27:
            break

cv.destroyAllWindows()
#print(datos)

keyboard.release('p')
