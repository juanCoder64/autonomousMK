import cv2 as cv
import keras
import os
import csv
import numpy as np
import keyboard
import joblib
import mss
import adjust_screen
import detect

drive = False
getData = False
threshold = 25
err = 0

lastKeys = ""
model = keras.saving.load_model("./model/player.keras", compile=True)
sc = joblib.load('../../AppData/Roaming/JetBrains/PyCharm2024.1/extensions/com.intellij.database/sc.joblib')

low = np.array([0, 0, 63])
high = np.array([38, 53, 124])
tLow = np.array([53, 173, 108])
tHigh = np.array([56, 202, 255])
iLow = np.array([58, 205, 241])
iHigh = np.array([162, 255, 255])
vHigh = np.array([0, 255, 195])
vLow = np.array([0, 255, 195])

# check if setup has been run
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
            drive = True

        if keyboard.is_pressed('g'):
            drive = False
            detData = False

        if keyboard.is_pressed('r'):
            getData = True

        center = (int((monitor["width"]) / 2), int((monitor["height"]) / 2))
        roadView = frame[int(h * .2):int(h * .35), int(w * .3):int(w * .7)]
        hsv = cv.cvtColor(roadView, cv.COLOR_BGR2HSV)
        playerView = frame[int(h * .3):int(h * .4), int(w * .4):int(w * .6)]
        fhsv = cv.cvtColor(playerView, cv.COLOR_BGR2HSV)

        # features detection
        roadX, err = detect.road(hsv, low, high, err, roadView)
        if err == 1:
            getData = False
        cv.imshow("playerView", playerView)
        pCloser, playerView = detect.features("pipe", tLow, tHigh, playerView, fhsv)  #get closest pipe
        iCloser, playerView = detect.features("itembox", iLow, iHigh, playerView, fhsv)  #get closest itembox

        # write to csv
        data = [roadX, pCloser * (pCloser != 50000), iCloser * (iCloser != 50000)]
        keysPressed = [keyboard.is_pressed('a'), keyboard.is_pressed('d'), keyboard.is_pressed('m'),
                       keyboard.is_pressed('k'), keyboard.is_pressed('l')]
        for j in range(len(keysPressed)):
            keysPressed[j] = int(keysPressed[j])
        if getData:
            with open("data.csv", "a", newline='') as d:
                writer = csv.writer(d)
                writer.writerows([data + keysPressed])
        cv.imshow('contours', frame)
        cv.imshow('roadView', roadView)

        # infer key presses
        data = np.array(data).reshape(-1, 3)
        #print(data)
        if drive:
            treshold = .95
            #keyboard.release('p')

            keys = "m"
            predictions = model(data)
            predictions = predictions.numpy()
            predictions = predictions[0]
            print(predictions, predictions[0] > treshold)
            if predictions[0] > treshold and predictions[1] > treshold:
                if predictions[0]-predictions[1] > 0:
                    keys += ",a"
                else:
                    keys += ",d"
            elif predictions[0] > treshold:
                keys += ",a"
            elif predictions[1] > treshold:
                keys += ",d"

            if predictions[3] > treshold:
                keys += ",k"
            if predictions[4] > treshold:
                keys += ",l"
            if err:
                keys=""
            for c in lastKeys:
                if c not in keys:
                    keyboard.release(c)
            if len(keys) != 0:
                print(keys)
                keyboard.send(keys, True, False)
            lastKeys = keys
        if cv.waitKey(20) == 27:
            break

cv.destroyAllWindows()
keyboard.release('x')
