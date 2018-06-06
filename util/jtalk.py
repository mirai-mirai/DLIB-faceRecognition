#! /usr/bin/python
# coding:utf-8

import subprocess as sp
import threading


def talk(text, voiceType=0):
    commands = []
    commands.append("/home/nttcom/faceRecognition/util/jtalk-angry.sh ")
    commands.append("/home/nttcom/faceRecognition/util/jtalk-happy.sh ")
    commands.append("/home/nttcom/faceRecognition/util/jtalk-sad.sh ")
    commands.append("/home/nttcom/faceRecognition/util/jtalk-mikuA.sh ")
    commands.append("/home/nttcom/faceRecognition/util/jtalk.sh ")
    assert voiceType < len(commands)

    sp.call([commands[voiceType] + text], shell=True)


def threadTalk(text, voiceType=0):
    threading.Thread(target=talk, args=(text, voiceType)).start()


if __name__ == '__main__':
    talk('これはテストです。', 0)

    #talk('不審人物が現れました。鈴木です。警戒してください。', 0)
    #talk("VIPがいらっしゃいました。山本さんです。最大のおもてなしをお願いします。", 1)
    #talk("それはとても悲しいですね。", 2)
