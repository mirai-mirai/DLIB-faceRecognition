# coding:utf-8

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2


def toStr(text):
    if isinstance(text, str):
        return text

    return text.encode('utf-8')


def toUnicode(text):
    if isinstance(text, bytes):
        return text

    return text.decode('utf-8')


class drawKanji():
    def __init__(self, fontSize=30):
        self.fontPath = '/etc/alternatives/fonts-japanese-gothic.ttf'
        self.fontSize = fontSize
        self.setFont(fontSize)

    def setFont(self, fontSize):
        self.font = ImageFont.truetype(self.fontPath, fontSize, encoding='unic')
        self.fontSize = fontSize

    def drawText(self, img, text, x, y, fontSize=0, color="#FFFFFF"):
        #assert isinstance(text, str) or isinstance(text, unicode)
        if fontSize > 0: self.setFont(fontSize)
        #if isinstance(text, str): text = text.decode('utf-8')
        img_pil = Image.fromarray(img)
        ImageDraw.Draw(img_pil).text((x, y), text, font=self.font, fill=color)
        return np.array(img_pil)


def test():
    kanji = drawKanji()
    cap = cv2.VideoCapture(0)

    size = 10

    while 1:
        ret, img = cap.read()

        size = 10 if size > 100 else size + 1
        text = '塩崎%d' % size

        img = kanji.drawText(img, text, 0, 0, fontSize=size)
        cv2.imshow('', img)
        if cv2.waitKey(1) & 0xff == ord('q'): break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    test()
