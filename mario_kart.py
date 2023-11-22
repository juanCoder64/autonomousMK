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
lx=70
err=0
Rvals=[]
hold=0
def nothing ():
    pass

def recalc(fr):
    print("new road calculated")
    cy=int(fr.shape[0]/2)
    cx=int(fr.shape[1]/2)
    delta=0
    img=fr[cy-10:cy+10,cx-10:cx+10]
    #img=cv.GaussianBlur(img,(51,51),0)
    img=cv.cvtColor(img,cv.COLOR_BGR2HSV)
    hue=np.min(img[:,:,0])-delta
    sat=np.min(img[:,:,1])-delta
    val=np.min(img[:,:,2])-delta
    low=np.array([hue,sat,val])
    hue=np.max(img[:,:,0])+delta
    sat=np.max(img[:,:,1])+delta
    val=np.max(img[:,:,2])+delta
    high=np.array([hue,sat,val])
    cv.imshow("Ncolor",img)
    return low,high
    
def detect(hsv, low, high, err):
    rd=cv.GaussianBlur(hsv,(11,11),0)
    rd=cv.inRange(rd,low,high)
    cnt,_=cv.findContours(rd, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    rx=0
    closer=50000
    R=None
    area=0
    for c in cnt:
            M = cv.moments(c)
            if M["m00"] != 0:
                RCx = int(M["m10"] / M["m00"])
                x, y, w, h = cv.boundingRect(c)
                if abs(RCx-100)<closer:# and w*h>3500:
                    closer=abs(RCx-100)
                    rx=RCx
                    R=c
    if R is not None:
        cv.drawContours(recorte, [R], -1, (120, 255, 0), 2)
        cv.circle(recorte, (rx, 25), 40, (255, 0, 0), 2)
        area=cv.contourArea(R)

    else:
        #recalculate min and max
        print("road not found!" )
        err+=1
    if area < 100:
        err+=1
    return rx,err

def roadfeatures(str, low, high, img, hsv):
    filtro = cv.inRange(hsv,low, high)
    filtro = cv.dilate(filtro, (15,15), iterations=3)
    closer =50000
    cnts = cv.findContours(filtro, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for c in cnts:
        cY=0 
        cX=0
        M = cv.moments(c)
        if  M["m00"] !=0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #cv.drawContours(recorte, [c], -1, (0, 255, 0), 2)
        if abs(cX-wo2) <= abs(closer):
            closer=cX-wo2
            cv.circle(img, (cX, cY), 7, (255, 255, 255), -1)
            cv.putText(img, str, (cX - 20, cY - 20),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
    return closer, frecorte


cv.namedWindow('sliders')
cv.createTrackbar('tresh','sliders' , 0, 255, nothing)
cv.createTrackbar('min','sliders' , 0, 255, nothing)
cv.createTrackbar('max','sliders' , 0, 255, nothing)
low = np.array([0, 0, 63])
high = np.array([38, 53, 124])
tLow = np.array([53, 173, 108])
tHigh = np.array([56, 202, 255])
iLow = np.array([58, 205, 241])
iHigh = np.array([162, 255, 255])
vHigh= np.array([0,255,195])
vLow= np.array([0,255,195])

with mss.mss() as sct:
    while "Screen capturing":
        monitor = {"top":391, "left":119, "width": 444, "height":332}
        img = np.array(sct.grab(monitor))   
        screen = np.array(sct.grab({"top":0, "left":0, "width": 1366, "height":768}))
        screen = cv.resize(screen,(1366,768))
        
        if keyboard.is_pressed('h'):
            dale = True

        if keyboard.is_pressed('g'):
            dale = False

        keys = 'p'

        frame = img
        wo2 = 100
        ho2 = 100
        cy = int((monitor["height"])/2)
        cx = int((monitor["width"])/2)
        
        recorte = frame[cy-ho2:cy-int(ho2/2), cx-wo2:cx+wo2]
        hsv = cv.cvtColor(recorte, cv.COLOR_BGR2HSV)
        frecorte = frame[cy-50:cy-5, cx-wo2:cx+wo2]
        fhsv = cv.cvtColor(frecorte, cv.COLOR_BGR2HSV)
        
        #road detection
        rx, err=detect(hsv,low,high,err)
        cv.imshow("road",frecorte)
        #print(rx)
        if(err>5) or keyboard.is_pressed('j'):
            err=0
            #recalc
            low,high=recalc(frecorte)

        
        icloser, frecorte=roadfeatures("itembox",iLow,iHigh,frecorte,fhsv)
        tcloser, frecorte =roadfeatures("tubo",tLow,tHigh,frecorte,fhsv)

        vuelta=False

        diferenciaV=rx-wo2

        #vuelta
        diferenciaR = rx-wo2
        #print(tcloser,icloser,treshold)
        
        road=abs(diferenciaR) > treshold
        tubo= abs(tcloser)<10
        box=abs(icloser)<5
        if road or  tubo or box:
            if tubo:
                road=1

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
            
            if road :
                treshold=abs(diferenciaR)-1
            
        else:
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
        
        if len(keys) != 0 and dale:
            keyboard.send(keys, 1, 0)

        if cv.waitKey(20) == 27:
            break

cv.destroyAllWindows()
keyboard.release('x')