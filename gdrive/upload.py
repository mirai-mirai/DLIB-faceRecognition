# coding:utf-8

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import threading
from time import sleep


class G_Drive:

    def __init__(self):
        print('init')
        self.gauth = GoogleAuth()
        self.gauth.CommandLineAuth()
        self.drive = GoogleDrive(self.gauth)
        self.isRunning = False

    def upload(self, fname, mimeType):
        f = self.drive.CreateFile({'title': fname, 'mimeType': mimeType})
        f.SetContentFile(fname)
        f.Upload()

    # 特定フォルダのファイルリスト取得がなぜかうまくいかない。。。
    def getList(self, folderID=None):
        print('getList')
        if folderID:
            query = "'%s' in parents and trashed=false" % folderID
            return self.drive.ListFile({'q': query}).GetList()
        else:
            return self.drive.ListFile().GetList()

    def delete(self, file_id):
        f = self.drive.CreateFile({'id': file_id})
        f.Delete()

    def threadCheck(self):
        self.isRunning = True

        while self.isRunning:
            for f in self.getList():
                print(f['title'], f['id'])
                # f.Delete()

            sleep(1)

    def startCheck(self):
        threading.Thread(target=self.threadCheck, args=()).start()


if __name__ == '__main__':
    gdrive = G_Drive()

    gdrive.upload('test.jpg', 'image/jpeg')

    flist = gdrive.getList('1oHFBGMRo1MBZxpFD-NAwtRWMdh1U30pl')
    print(flist)

    flist = gdrive.getList()
    print(flist)

    for f in flist:
        print(f['title'], f['id'])

    # gdrive.startCheck()
