import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller
import pyautogui
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

detector = HandDetector(detectionCon=0.8)
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""

keyboard = Controller()

frameR = 600 # Frame Reduction
smoothening = 7
wCam, hCam = 1920, 1080
wScr, hScr = 1920, 1080
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0


def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img


#
# def drawAll(img, buttonList):
#     imgNew = np.zeros_like(img, np.uint8)
#     for button in buttonList:
#         x, y = button.pos
#         cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
#                           20, rt=0)
#         cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]),
#                       (255, 0, 255), cv2.FILLED)
#         cv2.putText(imgNew, button.text, (x + 40, y + 60),
#                     cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
#
#     out = img.copy()
#     alpha = 0.5
#     mask = imgNew.astype(bool)
#     print(mask.shape)
#     out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
#     return out


class Button():
    
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

while True:
    success, img = cap.read()
    
    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)
    img = drawAll(img, buttonList)

    

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(l)

                ## when clicked
                if l < 30:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text
                    sleep(0.15)

    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)



    # img = img[frameR:hCam-1, 2*frameR:wCam-1]
    # 2. Get the tip of the index and middle fingers
    cv2.rectangle(img, (2*frameR, frameR), (wCam, hCam),
    (255, 0, 255), 2)
    if len(lmList) != 0:
        # x1, y1 = lmList[8][1:]
        # x2, y2 = lmList[12][1:]
        x1, y1 = lmList[8]
        x2, y2 = lmList[12]
        # print(x1, y1, x2, y2)
    
        if (x1 <= 2*frameR or y1<=frameR):
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
            (255, 0, 0), 3)
            # 12. Display

            cv2.imshow("Image", img)
            cv2.waitKey(1)
            continue

    # 3. Check which fingers are up
    fingers = detector.fingersUp()
    # print(fingers)
    # cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
    # (255, 0, 255), 2)
    
    # 4. Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        # x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        # y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        x3 = np.interp(x1, (2*frameR, wCam), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam), (0, hScr))
        # 6. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening
    
        # 7. Move Mouse
        # autopy.mouse.move(wScr - clocX, clocY)
        pyautogui.moveTo(wScr-clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY
        
    # 8. Both Index and middle fingers are up : Clicking Mode
    if fingers[1] == 1 and fingers[2] == 1:
        # 9. Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img)
        # print(length)
        # 10. Click mouse if distance short
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
            15, (0, 255, 0), cv2.FILLED)
            # autopy.mouse.click()
            pyautogui.leftClick()
    
    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
    (255, 0, 0), 3)
    # 12. Display

    cv2.imshow("Image", img)
    cv2.waitKey(1)
