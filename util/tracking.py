
# coding:utf-8

# 一画面中のbbox一式を渡して一度にトラッキングを更新する
# 顔検知をしないときにもbboxを速度ベクトルから更新する


import time
import numpy as np
import cv2

targetImageSize = 100
emptyImage = np.zeros((targetImageSize, targetImageSize, 3))


class targetCls:

    def __init__(self, id, bbox, history=50, targetImage=None, confidence=-1):
        self.id = id
        self.name = None
        self.distance = 999
        self.bboxes = [bbox]
        self.startTime = time.time()
        self.updateTime = self.startTime
        self.centerPoints = [(int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2))]
        self.history = history
        self.pbox = bbox
        self.lastIou = 1
        self.confidence = confidence
        if targetImage is not None:
            self.updateTargetImage(targetImage, confidence=-1)
        self.updateCount = 0
        self.property = None
        self.isAlarmed = False

    def updateTargetImage(self, image, confidence=-1):
        assert image is not None and len(image.shape) == 3

        if confidence == -1 or confidence > self.confidence:
            if image.shape[0] == 0 or image.shape[1] == 0:
                self.targetImage = emptyImage
                return False
            else:
                self.targetImage = cv2.resize(image, (targetImageSize, targetImageSize))
                self.confidence = confidence
                return True

    def updateProperty(self, property, distance):
        if distance < self.distance:
            self.property = property
            self.distance = distance

    def updateBbox(self, bbox):
        assert isinstance(bbox, list) and len(bbox) == 4

        self.bboxes.insert(0, bbox)
        self.bboxes = self.bboxes[:self.history]

        self.centerPoints.insert(0, (int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2)))
        self.centerPoints = self.centerPoints[:self.history]

        self.updateTime = time.time()
        self.updateCount += 1

        if len(self.bboxes) > 1:
            self.vbox = [new - old for (new, old) in zip(self.bboxes[0][:], self.bboxes[1][:])]
            self.mbox = np.mean(self.bboxes, axis=0)

        vx = self.centerPoints[0][0] - self.centerPoints[1][0]
        vy = self.centerPoints[0][1] - self.centerPoints[1][1]
        x, y, x1, y1 = bbox

        self.pbox = [x + vx, y + vy, x1 + vx, y1 + vy]

    def getBbox(self):
        return self.bboxes[0]

    def iou(self, bbox):

        bbox1 = [float(x) for x in self.pbox]
        bbox2 = [float(x) for x in bbox]

        (x0_1, y0_1, x1_1, y1_1) = bbox1
        (x0_2, y0_2, x1_2, y1_2) = bbox2

        # get the overlap rectangle
        overlap_x0 = max(x0_1, x0_2)
        overlap_y0 = max(y0_1, y0_2)
        overlap_x1 = min(x1_1, x1_2)
        overlap_y1 = min(y1_1, y1_2)

        # check if there is an overlap
        if overlap_x1 - overlap_x0 <= 0 or overlap_y1 - overlap_y0 <= 0:
            return 0

        # if yes, calculate the ratio of the overlap to each ROI size and the unified size
        size_1 = (x1_1 - x0_1) * (y1_1 - y0_1)
        size_2 = (x1_2 - x0_2) * (y1_2 - y0_2)
        size_intersection = (overlap_x1 - overlap_x0) * (overlap_y1 - overlap_y0)
        size_union = size_1 + size_2 - size_intersection
        self.lastIou = size_intersection / size_union

        return self.lastIou


class trackingCls:
    def __init__(self, threashold=0.5, timeToLive=1):
        self.targets = []
        self.targets_history = []
        self.targets_history_length = 20
        self.threashold = threashold
        self.timeToLive = timeToLive
        self.target_count = 0

    def getSameTarget(self, bbox):
        assert type(bbox) == list and len(bbox) == 4
        for target in self.targets:
            if target.iou(bbox) > self.threashold:
                target.updateBbox(bbox)
                if target.updateCount == 3:
                    self.targets_history.insert(0, target)
                    self.targets_history = self.targets_history[:self.targets_history_length]
                return target
        return None

    def updateTargetImage(self, target, targetImage, confidence):
        assert targetImage is not None and confidence is not None
        target.updateTargetImage(targetImage, confidence)

    # return True if new target is added.
    def addTarget(self, bbox, targetImage, confidence):
        assert isinstance(bbox, list) and len(bbox) == 4
        assert targetImage is not None and confidence is not None

        target = self.getSameTarget(bbox)
        isAdded = False
        if target is None:
            target_id = '%05d' % self.target_count
            target = targetCls(target_id, bbox, targetImage=targetImage, confidence=confidence)
            self.targets.append(target)
            self.target_count += 1
            isAdded = True
        else:
            self.updateTargetImage(target, targetImage, confidence)

        return isAdded, target

    def updateTarget(self, bbox, targetImage=None, confidence=None):

        sameTarget = self.getSameTarget(bbox, targetImage, confidence)

        if sameTarget is None:
            newTarget = self.addTarget(bbox, targetImage, confidence)
            return newTarget
        else:
            self.updateTargetImage(sameTarget, targetImage, confidence)
            return sameTarget

    def garbageCollect(self):

        for target in self.targets:
            if time.time() > target.updateTime + self.timeToLive:
                self.targets.remove(target)
