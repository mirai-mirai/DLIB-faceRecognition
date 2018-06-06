import time
import cv2


class calcFps():

    def __init__(self, updateInterval=0.2):
        self.updateInterval = updateInterval
        self.count = 0
        self.countAll = 0
        self.updateTime = time.time()
        self.num = 0

    def update(self):
        self.count += 1
        self.countAll += 1
        elapsedTime = time.time() - self.updateTime
        if elapsedTime > self.updateInterval:
            self.num = self.count / elapsedTime
            self.updateTime = time.time()
            self.count = 0

    def disp(self, canvas, x=10, y=30):
        self.update()
        cv2.putText(canvas, "FPS: %.2f" % self.num, (x, y), cv2.FONT_ITALIC, 0.6, (255, 255, 255))


if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    fps = calcFps()

    while 1:
        _, f = cap.read()
        fps.disp(f)
        cv2.imshow('', f)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cv2.destroyAllWindows()
