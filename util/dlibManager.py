# coding:utf-8

import cv2
import math
import os
import pickle
import dlib


def getLastUpdateTime(rootDir):
    assert os.path.exists(rootDir)
    updateTime = 0
    for root, dirs, files in os.walk(rootDir):
        for f in files:
            fname_full = os.path.join(root, f)
            ctime = os.path.getctime(fname_full)
            mtime = os.path.getmtime(fname_full)
            atime = os.path.getatime(fname_full)
            time = max([ctime, mtime, atime])

            if time > updateTime:
                updateTime = time

    return updateTime


class person:
    def __init__(self, name, features, isBlack=False, isVIP=False, imgFace=None):
        assert isinstance(features, list) and len(features) > 0
        #if isinstance(name, str):
        #    name = name.decode('utf-8')
        self.name = name
        self.features = features
        self.isBlack = isBlack
        self.isVIP = isVIP
        self.imgFace = imgFace
        self.dispP1 = None
        self.dispP2 = None


class personManager:
    def __init__(self, dirFaces, dlibWrapper):
        self.dlibWrapper = dlibWrapper
        self.persons = []
        self.dirFaces = dirFaces
        self.loadFaces()

    def calcDistance(self, feature, person):
        assert len(person.features) > 0

        dist_min = 99999
        for feature2 in person.features:
            assert isinstance(feature2, list) and len(feature2) == 128, person.name
            dist = 0.0
            for x, y in zip(feature2, feature):
                dist += (x - y) ** 2
            if dist < dist_min and dist > 0.05:
                dist_min = dist
        return math.sqrt(dist_min)

    def findMostSimilarPerson(self, feature):
        d_min = 999
        p_min = None
        for p in self.persons:
            d = self.calcDistance(feature, p)
            if d < d_min:
                d_min = d
                p_min = p
        return p_min, d_min

    def loadFaces(self):

        if self.loadPickle():
            return

        dirFaces = self.dirFaces
        self.persons = []

        for fname in os.listdir(dirFaces):
            fname_full = os.path.join(dirFaces, fname)

            if os.path.isfile(fname_full):
                fname_base, fname_ext = os.path.splitext(fname)
                if not fname_ext.lower() in ['.jpg', '.jpeg', '.png']: continue
                print(fname_base)
                feature = self.extractFeatureFromFile(fname_full)
                if feature is None: continue
                self.persons.append(person(fname_base, [feature]))
                print("  success\n")

            else:
                print(fname)
                features = []
                flist = os.listdir(fname_full)

                isBlack, isVIP = False, False
                if "black" in flist: isBlack = True
                if "vip" in flist: isVIP = True
                imgFace = None

                for f in flist:
                    fname_base, fname_ext = os.path.splitext(f)
                    if not fname_ext.lower() in ['.jpg', '.jpeg', '.png']: continue
                    feature = self.extractFeatureFromFile(os.path.join(dirFaces, fname, f))
                    if feature is None: continue
                    if imgFace is None: imgFace = cv2.imread(os.path.join(dirFaces, fname, f))
                    features.append(feature)

                print('  %d features' % len(features))

                if len(features) == 0: continue
                self.persons.append(person(fname, features, isBlack=isBlack, isVIP=isVIP, imgFace=imgFace))
                print("  success\n")

            self.savePickle()

    def loadFacesFromDir(self, personName):
        dirFaces = self.dirFaces
        print('loadFacesFromDir')

        fname_full = os.path.join(dirFaces, personName)
        assert os.path.exists(fname_full)

        features = []
        flist = os.listdir(fname_full)

        isBlack, isVIP = False, False
        if "black" in flist: isBlack = True
        if "vip" in flist: isVIP = True
        imgFace = None

        for f in flist:
            fname_base, fname_ext = os.path.splitext(f)
            if not fname_ext.lower() in ['.jpg', '.jpeg', '.png']: continue
            f_full = os.path.join(dirFaces, personName, f)
            #if isinstance(f_full, bytes):
            #    f_full = f_full.encode('utf-8')

            feature = self.extractFeatureFromFile(f_full)
            if feature is None: continue
            if imgFace is None: imgFace = cv2.imread(f_full)
            features.append(feature)

        print('  %d features' % len(features))

        if len(features) == 0:
            print('extracting feature is failed.')
            return

        print('pseron.append', personName, isBlack, isVIP)

        self.persons.append(person(personName, features, isBlack=isBlack, isVIP=isVIP, imgFace=imgFace))
        print("  success\n")

        self.savePickle()

    def loadPickle(self):
        dirFaces = self.dirFaces
        updateTime = getLastUpdateTime(dirFaces)

        pkl_name = dirFaces + '.pkl'
        if os.path.exists(pkl_name):
            print('loading pickle data "%s" .' % pkl_name)
            with open(pkl_name, mode='rb')as f:
                self.persons, savedTime = pickle.load(f)
                if updateTime != savedTime: return False
                print('%i people found.' % len(self.persons))
                return True

        return False

    def savePickle(self):
        dirFaces = self.dirFaces
        updateTime = getLastUpdateTime(dirFaces)

        with open(dirFaces + '.pkl', mode='wb') as f:
            pickle.dump((self.persons, updateTime), f)

    def writeFeature(self, fname_full, feature):
        with open(fname_full, 'w') as f:
            for i, val in enumerate(feature):
                f.write(str(val) + '\n')

    def extractFeatureFromFile(self, imgFname):
        #if isinstance(imgFname, bytes):
        #    imgFname = imgFname.encode('utf-8')

        imgRGB = cv2.imread(imgFname)[:, :, ::-1]
        h, w = imgRGB.shape[:2]
        if h > 768 or w > 1280:
            minimize = min(768.0 / h, 1280.0 / w)
            imgRGB = cv2.resize(imgRGB, fx=minimize, fy=minimize)
            h, w = imgRGB.shape[:2]

        feature = self.dlibWrapper.extractFeature(imgRGB, 0, 0, w - 1, h - 1)
        if type(feature) is list and len(feature) == 128:
            return feature
        else:
            return None


class dlibManager:
    def __init__(self, dataPath="util"):
        cnn_model = os.path.join(dataPath, "mmod_human_face_detector.dat")
        sp_model = os.path.join(dataPath, "shape_predictor_5_face_landmarks.dat")
        face_model = os.path.join(dataPath, "dlib_face_recognition_resnet_model_v1.dat")

        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_model)
        self.detector = dlib.get_frontal_face_detector()
        self.getShape = dlib.shape_predictor(sp_model)
        self.facerec = dlib.face_recognition_model_v1(face_model)

    def findFaces(self, img):
        return self.cnn_face_detector(img, 1)

    def findFaces2(self, img1, img2):
        return self.cnn_face_detector([img1, img2], 1, batch_size=2)

    # this can detect frontal face only.
    def findFrontalFaces(self, img):
        return self.detector(img)

    def extractFeature(self, img, x, y, x2, y2):
        img_mini = img[y:y2, x:x2]
        shape = self.getShape(img_mini, dlib.rectangle(0, 0, x2 - x, y2 - y))
        feature = self.facerec.compute_face_descriptor(img_mini, shape, 10)
        return [val for val in feature]




def test_getLastUpdatetime():
    t = getLastUpdateTime('/home/nttcom/faceRecognition/faces')
    print('-' * 10)
    print(t)


def test():
    import calcFps
    import videoDevice as vd
    import stopWatch as sw

    @sw.stop_watch
    def find(img, dm):
        faces = dm.findFaces(img)
        return faces

    @sw.stop_watch
    def find2(img, dm):
        faces = dm.findFaces2(img, img)
        return faces

    @sw.stop_watch
    def findGray(img, dm):
        return dm.findFaces(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))

    dm = dlibManager('.')
    fps = calcFps.calcFps()

    cap = vd.captureDevice(0)

    cv2.namedWindow('', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)

    count = 0
    bboxes = []

    while 1:
        ret, img = cap.read()
        if not ret: break

        fps.update()

        if count % 5 == 0:
            bboxes = []
            faces = find(img, dm)
            #faces = find2(img, dm)[0]
            #faces=[]

            for face in faces:
                r = face.rect
                bboxes.append([(r.left(), r.top()), (r.right(), r.bottom())])

        for p1, p2 in bboxes:
            cv2.rectangle(img, p1, p2, (0, 0, 255), thickness=3)

        fps.disp(img)
        cv2.imshow('', img)
        if cv2.waitKey(1) & 0xff == ord('q'): break

        count += 1


if __name__ == '__main__':
    test()
