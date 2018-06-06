#! /usr/bin/env python
# -*- coding: utf-8 -*-


import cv2
import os
import numpy as np
import threading
import urllib.request, urllib.error
from socket import error as SocketError
import socket
import subprocess as sp


class ipCamera(object):

    def __init__(self, url="http://192.168.43.1:8080/shot.jpg"):
        self.url = url
        self.req = urllib2.Request(self.url)
        self.width, self.height = 0, 0
        ret, img = self.read()

        if ret: self.width, self.height = img.shape[:2]

    def read(self):
        try:
            response = urllib2.urlopen(self.req, timeout=1)
            data = response.read()
            img_array = np.asarray(bytearray(data), np.uint8)
            if len(img_array) == 0:
                return False, None

            img = cv2.imdecode(img_array, -1)
            if self.width == 0:
                self.width, self.height = img.shape[:2]

            return True, img

        except (urllib2.URLError,socket.timeout,socket.error):
            pass

        return False, None

    def reload(self):
        pass

    def release(self):
        pass


# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera
class ipWebCam(object):
    def __init__(self, url="http://192.168.1.4:8080/video"):

        self.url = url
        print ('Streaming ' + self.url)

        self.bytes = ''

    def read(self):

        stream = urllib2.urlopen(self.url)
        while 1:
            self.bytes += stream.read(1024)
            a = self.bytes.find('\xff\xd8')
            b = self.bytes.find('\xff\xd9')
            if a != -1 and b != -1:
                jpg = self.bytes[a:b + 2]
                self.bytes = self.bytes[b + 2:]
                return True, cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)


class ipWebCam2(object):
    def __init__(self, width, height, ip="192.168.1.4", port="8080"):
        self.hoststr = 'http://%s:%s/video' % (ip, port)
        self.width = width
        self.height = height
        self.pipe = sp.Popen(["ffmpeg",
                              "-i", self.hoststr,
                              "-loglevel", "quiet",
                              "-an",
                              "-f", "image2pipe",
                              "-pix_fmt", "bgr24",
                              "-vcodec", "rawvideo", "-"],
                             stdin=sp.PIPE, stdout=sp.PIPE)

    def read(self):
        raw_image = self.pipe.stdout.read(self.width * self.height * 3)
        return np.frombuffer(raw_image, dtype=np.uint8).reshape((self.height, self.width, 3))


class AndroidCamFeed:
    __bytes = ''
    __stream = None
    __isOpen = False
    __feed = None
    __bytes = ''
    __noStreamCount = 1
    __loadCode = cv2.IMREAD_COLOR

    def __init__(self, host):
        self.hoststr = 'http://' + host + '/video'
        try:
            AndroidCamFeed.__stream = urllib2.urlopen(self.hoststr, timeout=3)
            AndroidCamFeed.__isOpen = True
        except (SocketError, urllib2.URLError) as err:
            print( "Failed to connect to stream. \nError: " + str(err))
            self.__close()
        t = threading.Thread(target=self.__captureFeed)
        t.start()

    def __captureFeed(self):
        while AndroidCamFeed.__isOpen:
            newbytes = AndroidCamFeed.__stream.read(1024)
            if not newbytes:
                self.__noStream()
                continue
            AndroidCamFeed.__bytes += newbytes
            self.a = AndroidCamFeed.__bytes.find('\xff\xd8')
            self.b = AndroidCamFeed.__bytes.find('\xff\xd9')
            if self.a != -1 and self.b != -1:
                self.jpg = AndroidCamFeed.__bytes[self.a: self.b + 2]
                AndroidCamFeed.__bytes = AndroidCamFeed.__bytes[self.b + 2:]
                AndroidCamFeed.__feed = cv2.imdecode(np.fromstring(self.jpg,
                                                                   dtype=np.uint8),
                                                     AndroidCamFeed.__loadCode)
        return

    def __close(self):
        AndroidCamFeed.__isOpen = False
        AndroidCamFeed.__noStreamCount = 1

    def __noStream(self):
        AndroidCamFeed.__noStreamCount += 1
        if AndroidCamFeed.__noStreamCount > 10:
            try:
                AndroidCamFeed.__stream = urllib2.urlopen(
                    self.hoststr, timeout=3)
            except (SocketError, urllib2.URLError) as err:
                print("Failed to connect to stream: Error: " + str(err))
                self.__close()

    def isOpened(self):
        return AndroidCamFeed.__isOpen

    def read(self):
        if AndroidCamFeed.__feed is not None:
            return True, AndroidCamFeed.__feed
        else:
            return False, None

    def release(self):
        self.__close()


class captureDevice(object):

    def __init__(self, deviceID=0, width=640, height=480):
        self.deviceID = deviceID
        self.width = width
        self.height = height
        self.setup()

        self.format = self.cap.get(cv2.CAP_PROP_FORMAT)
        self.fourcc = self.cap.get(cv2.CAP_PROP_FOURCC)

    def setup(self):
        self.cap = cv2.VideoCapture(self.deviceID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self):
        if not self.cap.isOpened: self.setup()
        ret, frame = self.cap.read()
        return ret, frame

    def reload(self):
        return

    def release(self):
        return


class captureVideoFile(object):
    def __init__(self, fname):
        assert os.path.exists(fname)
        self.fname = fname
        self.cap = cv2.VideoCapture(fname)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.numFrames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def reload(self):
        self.release()
        self.cap = cv2.VideoCapture(self.fname)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            self.reload()
            ret, frame = self.cap.read()

        return ret, frame

    def release(self):
        if self.cap.isOpened(): self.cap.release()


def getDevice(type=0):
    if type == 0:
        return captureDevice()
    elif type == 1:
        return captureDevice(deviceID=0, width=1280, height=720)
    elif type == 2:
        return captureDevice(deviceID=0, width=1920, height=1080)
    elif type == 3:
        return captureDevice(deviceID=0, videoFileName="input.mp4")
    elif type == 4:
        return ipCamera("http://192.168.43.1:8080/shot.jpg")
    elif type == 5:
        return ipCamera("http://192.168.11.4:8080/IMAGE")
    elif type == 6:
        return ipCamera("http://192.168.1.4:8080/shot.jpg")


################################

def test_p2p():
    server = ["192.168.43.1:8080", "192.168.11.4:8080", "192.168.1.4:8080"][0]
    url = ["http://%s/shot.jpg" % server, "http://%s/IMAGE" % server][0]
    print(url)

    cap_list = [ipCamera(url), ipWebCam(url)]

    cap_idx = 0
    cap = cap_list[cap_idx]
    imgEmpty = np.zeros((100, 100, 3), dtype=np.uint8)

    while 1:
        ret, frame = cap.read()
        imgScreen = frame if ret else imgEmpty
        cv2.imshow('', imgScreen)

        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        elif key == ord('c'):
            cap_idx += 1
            if cap_idx > len(cap_list) - 1: cap_idx = 0
            cap = cap_list[cap_idx]
            print("camera:%s" % cap_idx)


def test_camfeed():
    host = "192.168.43.1:8080"
    camfeed = AndroidCamFeed(host)
    while not camfeed.isOpened(): continue

    while 1:
        ret, img = camfeed.read()
        if ret: cv2.imshow("", img)
        if cv2.waitKey(100) & 0xff == ord('q'): break

    camfeed.release()


if __name__ == '__main__':
    test_p2p()
    # test_camfeed()

# cap = captureDevice(deviceID=0)
