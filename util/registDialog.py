# coding:utf-8

import tkinter as tk
from PIL import Image, ImageTk


class CustomDialog(tk.Toplevel):
    def __init__(self, root, imgFname):
        tk.Toplevel.__init__(self, root)

        self.nameString = tk.StringVar()
        self.choice = tk.IntVar()
        self.choice.set(0)

        titleFont = ('Helvetica', '15', 'bold')
        nameFont = ('Helvetica', '13', 'bold')

        self.titleLabel = tk.Label(self, text=u"【ユーザ登録】", font=titleFont)
        self.nameFrame = tk.Frame(self)
        self.nameLabel = tk.Label(self.nameFrame, text=u"名前", font=nameFont)
        self.nameEntry = tk.Entry(self.nameFrame, textvariable=self.nameString, font=nameFont)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok, width=10)
        self.cancell_button = tk.Button(self, text="Cancel", command=self.on_cancel, width=10)
        self.img = ImageTk.PhotoImage(Image.open(imgFname))
        self.imgLabel = tk.Label(self, image=self.img)

        self.radioFrame = tk.Frame(self)
        self.radio1 = tk.Radiobutton(self.radioFrame, text="NORMAL", variable=self.choice, value=0)
        self.radio2 = tk.Radiobutton(self.radioFrame, text="BLACK", variable=self.choice, value=1)
        self.radio3 = tk.Radiobutton(self.radioFrame, text="VIP", variable=self.choice, value=2)

        self.titleLabel.pack(side="top", fill="x", pady=5)
        self.imgLabel.pack(side="top", fill="x", padx=10, pady=5)

        self.nameFrame.pack(side="top")
        self.nameLabel.pack(side="left")
        self.nameEntry.pack(side="right")

        self.radioFrame.pack(side="top", pady=10)

        self.radio1.pack(side="left")
        self.radio2.pack(side="left")
        self.radio3.pack(side="left")

        self.ok_button.pack(side="left", expand=1, pady=10)
        self.cancell_button.pack(side="right", expand=1, pady=10)
        self.nameEntry.bind("<Return>", self.on_ok)

    def on_ok(self, event=None):
        self.destroy()

    def on_cancel(self, event=None):
        self.nameString.set('')
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.nameEntry.focus_force()
        self.wait_window()
        return self.nameString.get(), self.choice.get()


class DialogManager():
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_geometry('0x0')

    def showDialog(self, imgFname):
        return CustomDialog(self.root, imgFname).show()


if __name__ == "__main__":
    dm = DialogManager()
    name, choice = dm.showDialog(u"/home/nttcom/faceRecognition/faces/塩崎/1525260805823.jpg")
    name, choice = dm.showDialog(u"/home/nttcom/faceRecognition/faces/塩崎/1525260805823.jpg")
