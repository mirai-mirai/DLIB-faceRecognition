#! /usr/bin/env python
# coding:utf-8
# 顔画像のコントラスト補正


import os
import cv2
import time
import numpy as np
import shutil
from datetime import datetime
from util import tracking as trkCls
from util import videoDevice as vd
from util import calcFps
from util import dlibManager
from util import drawKanji as dk
from util import jtalk
from util import registDialog as rd

font = cv2.FONT_ITALIC
white = (255, 255, 255)


class ImgScreen:
    imgScreen = None

    def __init__(self, img):
        self.imgScreen = img


class gamma(object):
    def __init__(self, gamma=1.8):
        self.makeGammaTable(gamma)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def makeGammaTable(self, gamma):
        self.lookUpTable = np.zeros((256, 1), dtype='uint8')
        for i in range(256):
            self.lookUpTable[i][0] = 255 * pow(float(i) / 255, 1.0 / gamma)

    def applyGamma(self, img):
        return cv2.LUT(img, self.lookUpTable)

    def applyCahe(self, img):
        return self.clahe.apply(img)

    def enhance(img, clip_limit=3):
        image_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # split the image into L, A, and B channels
        l_channel, a_channel, b_channel = cv2.split(image_lab)

        # apply CLAHE to lightness channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)

        # merge the CLAHE enhanced L channel with the original A and B channel
        merged_channels = np.array(cv2.merge((cl, a_channel, b_channel)))

        # convert iamge from LAB color model back to RGB color model
        return cv2.cvtColor(merged_channels, cv2.COLOR_LAB2BGR)


def picInPic(imgBig, imgSmall, x, y):
    bh, bw = imgBig.shape[:2]
    sh, sw = imgSmall.shape[:2]
    assert bh > sh and bw > sw
    assert x < bw and y < bh

    if x + sw > bw: x = bw - sw
    if y + sh > bh: y = bh - sh

    imgBig[y:y + sh, x:x + sw] = imgSmall


def nothing(obj):
    pass


def main():
    FACE_DIR = "faces"
    dm = dlibManager.dlibManager()
    pm = dlibManager.personManager(FACE_DIR, dm)
    imgScreen = np.zeros((1000, 1920, 3), np.uint8)
    ImgScreen.imgScreen = imgScreen

    kanji = dk.drawKanji(18)

    cap_list = []
    cap_list.append(vd.captureVideoFile("rtt.mp4"))
    cap_list.append(vd.captureVideoFile("street-short.mp4"))
    cap_list.append(vd.captureVideoFile("tokyo-short.mp4"))
    cap_list.append(vd.captureDevice(deviceID=0, width=1280, height=780))
    cap_list.append(vd.captureDevice(deviceID=1, width=1280, height=780))
    # cap_list.append(vd.ipCamera("http://192.168.43.1:8080/shot.jpg"))

    cap_idx = 0
    cap = cap_list[cap_idx]

    targetImageSize = trkCls.targetImageSize

    captureSize = 'videoSize: %d x %d' % (cap.width, cap.height)

    WIN_NAME = 'w'
    cv2.namedWindow(WIN_NAME, flags=cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)

    cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.createTrackbar('Minimize', WIN_NAME, 10, 100, nothing)
    cv2.createTrackbar('Threshold', WIN_NAME, 33, 100, nothing)

    fps = calcFps.calcFps()
    trk = trkCls.trackingCls(threashold=0.3, timeToLive=0.3)

    HISTORY_DIR = 'history'
    SAVE_DIR = datetime.now().strftime("%Y%m%d_%H%M%S")

    screenHeight, screenWidth = imgScreen.shape[:2]

    imgTitle = cv2.imread("img/title.png")
    imgLogo1 = cv2.imread("img/blacklist.png")
    imgLogo2 = cv2.imread("img/viplist.png")

    picInPic(imgScreen, imgTitle, 30, 30)
    xMargin, yMargin = 10, 150
    picInPic(imgScreen, imgLogo1, xMargin, yMargin)
    picInPic(imgScreen, imgLogo2, screenWidth - imgLogo2.shape[1] - xMargin, yMargin)

    dialogManager = rd.DialogManager()

    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            if y < screenHeight - targetImageSize:
                return
            id = x // targetImageSize
            target = trk.targets_history[id]
            fdir = os.path.join(HISTORY_DIR, SAVE_DIR, target.id)

            fname_full = ''
            for fname in os.listdir(fdir):
                fname_base, fname_ext = os.path.splitext(fname)
                if not fname_ext.lower() in ['.jpg', '.jpeg', '.png']: continue
                fname_full = os.path.join(fdir, fname)

            name, choice = dialogManager.showDialog(fname_full)

            if not name:
                print('Operation:add-user canceled')
                return

            copyDir = os.path.join(FACE_DIR, name)
            shutil.copytree(fdir, copyDir)
            if choice == 1:
                with open(os.path.join(copyDir, "black"), "w"):
                    pass
            elif choice == 2:
                with open(os.path.join(copyDir, "vip"), "w"):
                    pass

            pm.loadFacesFromDir(name)

            ImgScreen.imgScreen = updateBlackVIP(ImgScreen.imgScreen)

    cv2.setMouseCallback(WIN_NAME, mouse_event)

    # draw blacklist and viplist
    def drawThumbnail(x, y, p, img):
        imgFace = cv2.resize(p.imgFace, (100, 100))
        p.dispP1 = (x - 10, y - 10)
        p.dispP2 = (x + 110, y + 125)
        cv2.rectangle(img, p.dispP1, p.dispP2, (50, 50, 50), -1)
        picInPic(img, imgFace, x, y)
        return kanji.drawText(img, p.name, x, y + 102, fontSize=19)

    specialPersons = []

    def updateBlackVIP(imgScreen):
        img = imgScreen
        blackList = [p for p in pm.persons if p.isBlack]
        for i, p in enumerate(blackList):
            x, y = 20, i * 140 + 250
            img = drawThumbnail(x, y, p, img)

        vipList = [p for p in pm.persons if p.isVIP]
        for i, p in enumerate(vipList):
            x, y = 1650, i * 140 + 250
            img = drawThumbnail(x, y, p, img)

        specialPersons.extend(blackList)
        specialPersons.extend(vipList)
        return img

    ImgScreen.imgScreen = updateBlackVIP(imgScreen)

    isPause = False
    blackScreen = np.zeros((720, 1280, 3), dtype=np.uint8)

    while 1:

        while isPause:
            if cv2.waitKey(10) & 0xff == ord('p'):
                isPause = False

        ret, imgOrigin = cap.read()
        if not ret: imgOrigin = blackScreen.copy()

        imgScreen = ImgScreen.imgScreen

        minimize = cv2.getTrackbarPos('Minimize', WIN_NAME) / 10.0 + 1
        threshold = cv2.getTrackbarPos('Threshold', WIN_NAME) / 100.0

        fps.update()
        imgCopy = imgOrigin.copy()
        imgRGB = imgOrigin[:, :, ::-1]
        imgRGB_resized = cv2.resize(imgRGB, (0, 0), fx=1.0 / minimize, fy=1.0 / minimize)

        # find faces from screen
        faces = dm.findFaces(imgRGB_resized)

        # check every face with tracking data
        for i, face in enumerate(faces):
            r = face.rect
            x, y, = int(r.left() * minimize), int(r.top() * minimize)
            x2, y2 = int(r.right() * minimize), int(r.bottom() * minimize)
            if x < 0 or y < 0: continue
            c = face.confidence
            imgFace = imgOrigin[y:y2, x:x2]

            bbox = [x, y, x2, y2]

            isAdded, target = trk.addTarget(bbox, imgFace, c)

            # save detected face image
            fdir = os.path.join(HISTORY_DIR, SAVE_DIR, target.id)
            if not os.path.exists(fdir):
                os.makedirs(fdir)
                fname = os.path.join(HISTORY_DIR, SAVE_DIR, '%s.jpg' % target.id)
                cv2.imwrite(fname, imgFace)

            fname = os.path.join(fdir, '%s.jpg' % int(time.time() * 1000))
            cv2.imwrite(fname, imgFace)

            # not check feature if the image is too small
            if x2 - x < 80 and y2 - y < 80: continue

            # detect feature and compare with known faces
            feature = dm.extractFeature(imgRGB, x, y, x2, y2)
            similarPerson, distance = pm.findMostSimilarPerson(feature)
            if distance < threshold:
                target.updateProperty(similarPerson, distance)

        # clear specialPersons frame
        def drawSpecialPersonFrame(person, color):
            cv2.rectangle(imgScreen, person.dispP1, person.dispP2, color, thickness=2)

        for person in specialPersons:
            drawSpecialPersonFrame(person, (0, 0, 0))

        # draw every target
        isBlack, isVIP = False, False
        for i, target in enumerate(trk.targets):
            if target.updateCount < 3: continue
            b, v = False, False
            person = target.property
            if person is not None:
                if person.isBlack:
                    isBlack = True
                    b = True
                    drawSpecialPersonFrame(person, (0, 0, 255))
                    if not target.isAlarmed:
                        msg = u'不審人物があらわれました。%sです。' % person.name
                        jtalk.threadTalk(msg, 0)
                        target.isAlarmed = True
                if person.isVIP:
                    isVIP = True
                    v = True
                    drawSpecialPersonFrame(person, (0, 0, 255))
                    if not target.isAlarmed:
                        msg = u'VIPがいらっしゃいました。%sさんです。最大限のおもてなしをしてください。' % person.name
                        jtalk.threadTalk(msg, 1)
                        target.isAlarmed = True

            color = (255, 255, 255)
            if b: color = (0, 0, 255)
            if v: color = (41, 148, 207)

            x, y, x2, y2 = target.getBbox()
            cv2.rectangle(imgCopy, (x, y), (x2, y2), color, -1)
            cv2.putText(imgOrigin, '%d x %d' % (x2 - x, y2 - y), (x, y2 + 15), font, 0.4, (0, 0, 255))

            labelName = person.name if person else target.id
            imgOrigin = kanji.drawText(imgOrigin, labelName, x, y - 25, fontSize=25)

            # draw line of target
            for i, pt in enumerate(target.centerPoints):
                if i > 0:
                    cv2.line(imgCopy, pt, last_pt, (255, 255, 0), thickness=2)
                last_pt = pt

        trk.garbageCollect()
        cv2.putText(imgOrigin, "FPS: %.2f" % fps.num, (10, 30), font, 0.6, white)
        cv2.putText(imgOrigin, captureSize, (10, 45), font, 0.6, white)
        cv2.putText(imgOrigin, "%d frames" % fps.countAll, (10, 60), font, 0.6, white)

        imgMerged = cv2.addWeighted(imgOrigin, 0.7, imgCopy, 0.3, 0)

        # draw target history images on bottom of screen
        for i, target in enumerate(trk.targets_history):
            x = int(i * targetImageSize)
            y = int(screenHeight - targetImageSize)
            if x + targetImageSize > screenWidth:
                break

            imgScreen[y:y + targetImageSize, x:x + targetImageSize] = target.targetImage
            cv2.putText(imgScreen, target.id, (x + 10, y + 15), font, 0.5, white)
            person = target.property
            if person:
                imgScreen = kanji.drawText(imgScreen, person.name, x + 10, y + 18, fontSize=18)
                cv2.putText(imgScreen, '%.2f' % target.distance, (x + 10, y + 55), font, 0.5, white)
                if person.isBlack or person.isVIP:
                    if person.isBlack:
                        color = (0, 0, 255)
                    if person.isVIP:
                        color = (41, 148, 207)
                    cv2.rectangle(imgScreen, (x + 3, y + 3), (x + targetImageSize - 3, y + targetImageSize - 3), color,
                                  thickness=3)

        frameColor = (50, 50, 50)
        if isBlack and fps.countAll % 2 == 0:
            frameColor = (0, 0, 255)
        if isVIP and fps.countAll % 2 == 1:
            frameColor = (41, 148, 207)

        h, w = imgMerged.shape[:2]
        x, y = int((screenWidth - w) / 2), 150

        cv2.rectangle(imgScreen, (x, y), (x + w, y + h), frameColor, thickness=20)
        imgScreen[y:y + h, x:x + w] = imgMerged
        cv2.imshow(WIN_NAME, imgScreen)

        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        elif key == ord('c'):
            cap.release()
            cap_idx += 1
            if cap_idx > len(cap_list) - 1: cap_idx = 0
            cap = cap_list[cap_idx]
            cap.reload()
        elif key == ord('p'):
            isPause = True

    cv2.destroyAllWindows()
    for cap in cap_list:
        cap.release()


def test_gamma():
    img = cv2.imread('faces/青木.jpg')
    image_m = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    cv2.imshow('', img)
    cv2.waitKey(1000)
    g = gamma()
    print(type(img), img.shape)
    img2 = g.enhance(np.array(img))
    img3 = np.hstack((img, img2))
    cv2.imshow('', img3)
    cv2.waitkey(1000)

    exit(0)


if __name__ == "__main__":
    main()
