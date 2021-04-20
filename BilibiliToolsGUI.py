from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QPushButton, QAction, QLineEdit, QFileDialog
from bilibili.HotCommentWordCloud import VideoCommentWordCloud
from bilibili.Downloader import *
from bilibili.User import *
from bilibili.Animation import *

import os
import sys
import threading
import urllib
import time
import ctypes
import inspect
from PIL import Image, ImageQt
from PyQt5 import QtWidgets, QtGui, QtCore

# ----------------------- UTILS ------------------------ #
global root
root = None

def getHeaders(use_cookie=False):
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"",
    }
    if use_cookie:
        f = open("./cookie.txt", "r")
        headers['cookie'] = f.readline().strip('\n')
        f.close()
    return headers

def getColorText(string: str, color: str):
    return "<font color='{}'>{}<font>".format(color, string)

# find a layer in the gui
def find(class_name, layer):
    children = layer.childLyr
    if isinstance(layer, class_name):
        return layer
    for lyr in children:
        _ = find(class_name, lyr)
        if _ : return _
    return None

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
# ------------------------------------------------------ #


# -------------------- LOGIN WINDOW ---------------------#
class LoginWindow(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        # init root layer #
        global root
        root = self
        # --------------- #
        self.childLyr = []
        self.parentLyr = None
        self.mainWindow = None
        self.initUI()
        self.signal.connect(self.moveToMainWindow)
        self.login()
        self.show()

    def initUI(self):
        self.setFixedSize(320, 400)
        self.setWindowTitle("Login")
        # QRcode Image
        self.qrCodeImage = QtWidgets.QLabel(self)
        self.qrCodeImage.setGeometry(60, 60, 200, 200)
        self.qrCodeImage.setPixmap(QtGui.QPixmap("./data/resurce/qrcinit.png"))
        self.qrCodeImage.setScaledContents(True)
        # Login notice
        self.loginNotice = QtWidgets.QLabel(self)
        self.loginNotice.setGeometry(60, 300, 200, 20)
        self.loginNotice.setText("Please login in 120 second")
        self.loginNotice.setFont(QtGui.QFont("Microsoft YaHei"))
        self.loginNotice.setAlignment(QtCore.Qt.AlignCenter)
        # Skip Button
        self.skipBtn = QtWidgets.QPushButton(self)
        self.skipBtn.setGeometry(200, 350, 100, 30)
        self.skipBtn.setText("Skip")
        self.skipBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.skipBtn.clicked.connect(self.moveToMainWindow)

    def moveToMainWindow(self):
        try:
            stop_thread(self.th)
        except:
            pass
        headers = getHeaders(True)
        user = BilibiliUser(headers, "./api.cfg")
        info = user.get_account_info()
        if info is not None:
            urllib.request.urlretrieve(
                url=info['face'], 
                filename="./data/user/head.jpg")
            user_info = {
                "name": info['name'],
                "uid": str(info['mid']),
                "gender": info['sex'],
                "level": str(info['level']),
                "head": "./data/user/head.jpg"
            }
            self.qrCodeImage.setPixmap(QtGui.QPixmap("./data/resource/successful.png"))
            self.loginNotice.setText("Login successful ... ")
            QtWidgets.QApplication.processEvents()
            time.sleep(1.5)
        else:
            user_info = {
                "name": 'Guest',
                "uid": 'NONE',
                "gender": '男',
                "level": '0',
                "head": "./data/resource/login.png"
            }
        self.mainWindow = MainWindow(user_info, self)
        self.mainWindow.show()
        self.setVisible(False)
        
    def getLoginQRcode(self):
        headers = getHeaders()
        login_obj = LoginApp(headers, "./cookie.txt", "./api.cfg")
        img, qrcode_dict = login_obj.get_login_qrcode()
        img = ImageQt.toqpixmap(img)
        self.qrCodeImage.setPixmap(img)
        return login_obj, qrcode_dict
        
    def checkLogin(self, login_obj, qrcode_dict):
        status = login_obj.login(qrcode_dict, 120)
        if status:
            if login_obj.check_login():
                self.signal.emit(True)
    
    def login(self):
        self.loginNotice.setText("Please login in 120 second")
        login_obj, qrcode_dict = self.getLoginQRcode()
        self.th = threading.Thread(target=self.checkLogin, args=(login_obj, qrcode_dict,))
        self.th.start()

    def closeEvent(self, event):
        event.accept()
        os._exit(0)
# ------------------------------------------------------ #


# --------------------- MAIN WINDOW -------------------- #
class MainWindow(QtWidgets.QWidget):
    def __init__(self, user_info: dict, _parent):
        super().__init__()
        self.user_info = user_info
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(720, 480)
        self.setWindowTitle("Bilibili ToolBox")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QtGui.QIcon("./data/resource/main.ico"))
        # add component
        self.rightFuncBox = RightFuncBox(self)
        self.leftFuncBox = LeftFuncBox(self)
        # set layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.leftFuncBox, 0)
        layout.addWidget(self.rightFuncBox, 1)
        layout.setStretch(0, 5)
        layout.setStretch(1, 13)
        self.setLayout(layout)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            'Quit',
            "Are you sure to quit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()
# ------------------------------------------------------ #


# --------------- RIGHT FUNCTIONAL BOX ----------------- #
class RightFuncBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        # add component
        self.rightLogBox = RightLogBox(self)
        # self.rightOperationBox = RightDownloadBox(self)
        self.rightOperationBox = QtWidgets.QTabWidget(self)
        self.rightOperationBox.addTab(RightBlankBox(self), "blank") # 0
        self.rightOperationBox.addTab(RightVideoBox(self), "video") # 1
        self.rightOperationBox.addTab(RightDownloadBox(self), "download") # 2
        self.rightOperationBox.addTab(WordcloudPreview(self), "preview")  # 3
        self.rightOperationBox.addTab(RightWordcloudCreate(self), "createwordcloud")  # 4
        # self.rightOperationBox.addTab(RightAnimationPreview(self), "animationinfopreview")  # 5
        self.rightOperationBox.addTab(RightAnimationInfo(self), "animationinfocollect")  # 5
        self.rightOperationBox.setCurrentIndex(0)
        self.rightOperationBox.tabBar().hide()
        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.rightOperationBox, 0)
        layout.addWidget(self.rightLogBox, 1)
        layout.setStretch(0, 4)
        layout.setStretch(1, 1)
        self.setLayout(layout)

    def flipTabPage(self, name: str):
        if name == "video":
            self.rightOperationBox.setCurrentIndex(1)
        elif name == "download":
            self.rightOperationBox.setCurrentIndex(2)
        elif name == "preview":
            self.rightOperationBox.setCurrentIndex(3)
        elif name == "createwordcloud":
            self.rightOperationBox.setCurrentIndex(4)
        elif name == "animationinfocollect":
            self.rightOperationBox.setCurrentIndex(5)
        else:
            self.rightOperationBox.setCurrentIndex(0)

class RightBlankBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStretch(0, 1)
        self.setLayout(layout)

class RightVideoBox(QtWidgets.QLabel):
    infoSignal = QtCore.pyqtSignal(list)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.qu_dict = {
            '4K 超清': 120,
            '1080P 高码率': 112,
            '1080P 60帧': 112,
            '1080P 高清': 80,
            '720P 60帧': 64,
            '720P 高清': 64,
            '480P 清晰': 32,
            '360P 流畅': 16,
            '240P 极速': 6,
            'cover': 'cover'
        }
        self.qu_user = None
        self.infoSignal.connect(self.updateQuInfo)

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # link editor
        self.linkEdit = QtWidgets.QLineEdit(self)
        self.linkEdit.setGeometry(20, 50, 350, 30)
        self.linkEdit.setStyleSheet('''QLineEdit{
            border:1px solid gray;                
            border-radius:10px;         
            padding:2px 4px; }''')
        self.linkEdit.setPlaceholderText('请输入视频链接')
        # search
        self.searchBtn = QtWidgets.QPushButton(self)
        self.searchBtn.setGeometry(380, 50, 100, 30)
        self.searchBtn.setText("search")
        self.searchBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.searchBtn.clicked.connect(self.searchVideoInfo)
        # info 
        self.infoBox = QtWidgets.QTextBrowser(self)
        self.infoBox.setGeometry(20, 100, 460, 200)
        self.infoBox.setFont(QtGui.QFont("Microsoft YaHei"))
        # quality
        self.qualityBox = QtWidgets.QComboBox(self)
        self.qualityBox.setGeometry(260, 320, 100, 30)
        self.qualityBox.setFont(QtGui.QFont("Microsoft YaHei"))
        self.qualityBox.addItems(['none'])
        self.qualityBox.highlighted[str].connect(self.saveUserQu)  # please ignore the red line
        # downlaod
        self.downloadBtn = QtWidgets.QPushButton(self)
        self.downloadBtn.setGeometry(380, 320, 100, 30)
        self.downloadBtn.setText("download")
        self.downloadBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.downloadBtn.clicked.connect(self.download)
        # clear
        self.downloadBtn = QtWidgets.QPushButton(self)
        self.downloadBtn.setGeometry(140, 320, 100, 30)
        self.downloadBtn.setText("clear")
        self.downloadBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.downloadBtn.clicked.connect(self.clearAll)

    def searchVideoInfo(self):
        link = self.linkEdit.text()
        th = threading.Thread(target=self.infoThread, args=(link,))
        th.start()

    def saveUserQu(self, qu):
        if qu != "none":
            self.qu_user = 'cover' if self.qu_dict[qu] == 'cover' else int(self.qu_dict[qu])

    def infoThread(self, link):
        downloader = VideoDownloader(getHeaders(True), "./download/video", "./api.cfg")
        info_dict = downloader.get_video_info(link=link)
        qu = downloader.get_supported_quality(info_dict)
        self.infoSignal.emit([info_dict, qu])
    
    def updateQuInfo(self, quInfo):
        self.qualityBox.clear()
        for item in quInfo[1]:
            self.qualityBox.addItem(item[0])
        self.qualityBox.addItem('cover')
        self.infoBox.append("Video Information\n")
        self.infoBox.append("name: {}\nbvid: {}\n".format(
            quInfo[0]['title'], quInfo[0]['bvid']))

    def download(self):
        link = self.linkEdit.text()
        if self.qu_user != 'cover':
            downloader = VideoDownloader(getHeaders(True), "./download/video", "./api.cfg")
            info_dict = downloader.get_video_info(link=link)
            info_dict['d_type'] = 'video'
        else:
            downloader = CoverDownloader(getHeaders(True), "./download/image", "./api.cfg")
            info_dict = downloader.get_video_info(link=link)
            info_dict['d_type'] = 'cover'
        obj = find(RightDownloadBox, root).addDownload(info_dict)
        th = threading.Thread(
            target=self.downloadThread, args=(downloader, obj, info_dict,))
        obj.d_thread = th
        th.start()
        if self.qu_user != 'cover':
            self.parentLyr.rightLogBox.addLog(
                "start to download video {}".format(info_dict['bvid']), "green")
        else:
            self.parentLyr.rightLogBox.addLog(
                "start to download cover of {}".format(info_dict['bvid']), "green")
        
    def downloadThread(self, downloader, obj, info_dict):
        if isinstance(downloader, VideoDownloader):
            qu = 32 if self.qu_user is None else self.qu_user
            downloader.download_Video(
                info_dict, qu, 
                obj._progress)
        elif isinstance(downloader, CoverDownloader):
            downloader.download_Cover(
                info_dict,
                obj._progress
            )

    def clearAll(self):
        self.qu_user = None
        self.qualityBox.clear()
        self.qualityBox.addItem("none")
        self.linkEdit.clear()
        self.infoBox.clear()

class RightDownloadBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # download head
        self.downloadHead = DownloadHead(self)
        # download table
        self.downloadTable = QtWidgets.QTableWidget(0, 1, self)
        self.downloadTable.verticalHeader().setVisible(False)
        self.downloadTable.horizontalHeader().setVisible(False)
        self.downloadTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.downloadTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed) 
        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.downloadHead)
        layout.addWidget(self.downloadTable)
        layout.setStretch(0, 1)
        layout.setStretch(1, 8)
        self.setLayout(layout)

    # test
    def addDownload(self, info_dict):
        num = self.downloadTable.rowCount()
        self.downloadTable.setRowCount(num+1)
        self.downloadTable.setRowHeight(num, 80)
        obj = SingleDownloadBox(self, info_dict)
        self.downloadTable.setCellWidget(num, 0, obj)
        self.downloadHead.addTask()
        self.update()
        return obj

    def clearAll(self):
        self.downloadTable.clearContents()
        self.downloadTable.setRowCount(0)

class DownloadHead(QtWidgets.QLabel):
    signal = QtCore.pyqtSignal(float)
    signal2 = QtCore.pyqtSignal(dict)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.signal.connect(self.updateBar)
        self.signal2.connect(self.completeTask)
        self.tasksNum = 0
        self.tasksFinished = 0

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # info 
        self.info = QtWidgets.QLabel(self)
        self.info.setText("Tasks:  0/0")
        self.info.setFont(QtGui.QFont("Microsoft YaHei"))
        # total bar
        self.bar = QtWidgets.QProgressBar(self)
        self.bar.setMaximum(100)
        self.bar.setValue(0)
        # set layout
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.info)
        layout.addWidget(self.bar)
        layout.setStretch(0, 1)
        layout.setStretch(1, 5)
        self.setLayout(layout)

    def addTask(self):
        if self.tasksNum != 0:
            self.bar.setMaximum(self.bar.maximum()+100)
        self.tasksNum += 1
        self.info.setText("Tasks:  {}/{}".format(
            self.tasksFinished, self.tasksNum))
    
    def updateBar(self, percent):
        self.bar.setValue(int(self.bar.value()+percent))
        if percent < 0:
            self.bar.setMaximum(int(self.bar.maximum()-100))

    def resetHead(self):
        self.bar.setValue(0)
        self.info.setText("Tasks:  0/0")
        self.bar.setMaximum(100)
        self.tasksNum = 0
        self.tasksFinished = 0

    def completeTask(self, info_dict):
        d_type = info_dict['d_type']  # download type
        if info_dict['d_status']:
            self.parentLyr.parentLyr.rightLogBox.addLog(
                "{} of {} finished".format(d_type, info_dict['bvid']), "green")
            self.tasksFinished += 1
        else:
            self.parentLyr.parentLyr.rightLogBox.addLog(
                "{} of {} cancelled".format(d_type, info_dict['bvid']), "red")
            self.tasksNum -= 1
        if self.tasksFinished == self.tasksNum:
            self.resetHead()
            self.parentLyr.clearAll()
        else:
            self.info.setText("Tasks:  {}/{}".format(
                self.tasksFinished, self.tasksNum))

class SingleDownloadBox(QtWidgets.QLabel):
    signal = QtCore.pyqtSignal(float)
    def __init__(self, _parent, info_dict):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.info_dict = info_dict
        self.initUI(info_dict)
        self.d_head = 0
        self.d_thread = None
        self.status = None
        self.signal.connect(self.updateBar)

    def initUI(self, info_dict):
        # title
        self.title = QtWidgets.QLabel(self)
        self.title.setText("name:  %s"%info_dict['title'])
        self.title.setFont(QtGui.QFont("Microsoft YaHei"))
        self.title.setGeometry(10, 10, 380, 20)
        # bvid
        self.bvid = QtWidgets.QLabel(self)
        self.bvid.setText("bvid:  %s"%info_dict['bvid'])
        self.bvid.setFont(QtGui.QFont("Microsoft YaHei"))
        self.bvid.setGeometry(10, 30, 200, 20)
        # bar
        self.bar = QtWidgets.QProgressBar(self)
        self.bar.setGeometry(10, 60, 380, 10)
        self.bar.setMaximum(100)
        self.bar.setValue(0)
        self.bar.setStyleSheet('''QProgressBar {   
            border: 1px solid grey;   
            border-radius: 5px;   
            text-align: center;
            background-color: #F8F8FF;}
            QProgressBar::chunk {   
                background-color: #7B68EE;   }''')
        # cancel btn
        self.cancelBtn = QtWidgets.QPushButton(self)
        self.cancelBtn.setGeometry(400, 50, 80, 30)
        self.cancelBtn.setText("cancel")
        self.cancelBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.cancelBtn.clicked.connect(self.cancelTask)

    def _progress(self, blocknum, blocksize, totalsize):
        percent = 100 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        self.signal.emit(percent)

    def updateBar(self, percent):
        self.parentLyr.downloadHead.signal.emit(percent-self.bar.value())
        self.bar.setValue(int(percent))
        if int(percent) == 100:
            self.info_dict['d_status'] = True
            self.parentLyr.downloadHead.signal2.emit(self.info_dict)
    
    def cancelTask(self):
        stop_thread(self.d_thread)
        self.info_dict['d_status'] = False
        self.parentLyr.downloadHead.signal.emit(-self.bar.value())
        self.parentLyr.downloadHead.signal2.emit(self.info_dict)
        self.bar.setStyleSheet('''QProgressBar {   
            border: 1px solid grey;   
            border-radius: 5px;   
            text-align: center;
            background-color: #F8F8FF;}
            QProgressBar::chunk {   
                background-color: #FF0000;   }''')

class WordcloudPreview(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.downloadFolder = ""
        self.initUI()
    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        #lab1 = QLabel()
        #lab1.setPixmap(QPixmap("./download/wordcloud/new_demowordcloud.png").scaled(250, 400))
        self.selectPicture = QPushButton(self)
        self.selectPicture.setText("预览图片")
        self.selectPicture.setFont(QtGui.QFont("Microsoft YaHei"))
        self.selectPicture.setGeometry(380, 320, 100, 30)
        self.selectPicture.clicked.connect(self.openimage)

        self.openfile = QPushButton(self)
        self.openfile.setText("打开图片所在文件夹")
        self.openfile.setFont(QtGui.QFont("Microsoft YaHei"))
        self.openfile.setGeometry(190, 320, 180, 30)
        self.openfile.clicked.connect(self.openDownloadFolder)
        # preview picture
        self.previewPicture = QLabel(self)
        self.previewPicture.setText("                 '此处预览'")
        #self.previewPicture.setFixedSize(100, 80)
        self.previewPicture.setGeometry(20, 30, 470, 235)
        self.previewPicture.setStyleSheet("QLabel{background:white;}"
                                 "QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;font-family:宋体;}"
                                 )
        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStretch(0, 1)
        #layout.addWidget(lab1)
        self.setLayout(layout)

    def openDownloadFolder(self):
        self.getDownloadPath()
        os.startfile(self.downloadFolder)

    def getDownloadPath(self):
        self.downloadFolder = os.path.join(
            os.path.abspath(os.path.dirname(sys.argv[0])),
            "./download/wordcloud")

    def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "./download/wordcloud", "*.png;;*.jpg;;All Files(*)")
        jpg = QtGui.QPixmap(imgName).scaled(self.previewPicture.width(), self.previewPicture.height())
        self.previewPicture.setPixmap(jpg)

class RightWordcloudCreate(QtWidgets.QLabel):
    infoSignal = QtCore.pyqtSignal(list)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.downloadFolder = ""
        self.initUI()
        self.infoSignal.connect(self.updateQuInfo)

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)

        # link editor
        self.linkEdit = QtWidgets.QLineEdit(self)
        self.linkEdit.setGeometry(20, 50, 350, 30)
        self.linkEdit.setStyleSheet('''QLineEdit{
                    border:1px solid gray;                
                    border-radius:10px;         
                    padding:2px 4px; }''')

        self.linkEdit.setPlaceholderText('请输入bvid')
        action = QAction(self)
        action.setIcon(QIcon('./data/resource/bk8.png'))
        self.linkEdit.addAction(action, QLineEdit.TrailingPosition)
        # search
        self.searchBtn = QtWidgets.QPushButton(self)
        self.searchBtn.setGeometry(380, 50, 100, 30)
        self.searchBtn.setText("search")
        self.searchBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.searchBtn.clicked.connect(self.searchVideoInfo)
        # info
        self.infoBox = QtWidgets.QTextBrowser(self)
        self.infoBox.setGeometry(20, 100, 460, 200)
        self.infoBox.setFont(QtGui.QFont("Microsoft YaHei"))
        # create
        self.createBtn = QtWidgets.QPushButton(self)
        self.createBtn.setGeometry(380, 320, 100, 30)
        self.createBtn.setText("生成词云")
        self.createBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.createBtn.clicked.connect(self.createWordcloud)
        # select picture
        '''self.selectPicture = QPushButton(self)
        self.selectPicture.setText("打开图片")
        self.selectPicture.setFont(QtGui.QFont("Microsoft YaHei"))
        self.selectPicture.setGeometry(270, 320, 100, 30)
        self.selectPicture.clicked.connect(self.openimage)'''
        # preview picture
        '''self.previewPicture = QLabel(self)
        self.previewPicture.setText("'预览'")
        self.previewPicture.setFixedSize(100, 80)
        self.previewPicture.setGeometry(140, 270, 100, 30)
        self.previewPicture.setStyleSheet("QLabel{background:white;}"
                                 "QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;font-family:宋体;}"
                                 )
                                 '''
        # openfile
        self.clearBtn = QtWidgets.QPushButton(self)
        self.clearBtn.setGeometry(70, 320, 180, 30)
        self.clearBtn.setText("打开图片所在文件夹")
        self.clearBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.clearBtn.clicked.connect(self.openDownloadFolder)
        # clear
        self.clearBtn = QtWidgets.QPushButton(self)
        self.clearBtn.setGeometry(260, 320, 100, 30)
        self.clearBtn.setText("clear")
        self.clearBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.clearBtn.clicked.connect(self.clearAll)

    '''def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        jpg = QtGui.QPixmap(imgName).scaled(self.previewPicture.width(), self.previewPicture.height())
        self.previewPicture.setPixmap(jpg)'''

    def searchVideoInfo(self):
        link = "https://www.bilibili.com/video/" + self.linkEdit.text()
        th = threading.Thread(target=self.infoThread, args=(link,))
        th.start()
    def infoThread(self, link):
        downloader = VideoDownloader(getHeaders(True), "./download/video", "./api.cfg")
        info_dict = downloader.get_video_info(link=link)
        qu = downloader.get_supported_quality(info_dict)
        self.infoSignal.emit([info_dict, qu])

    def updateQuInfo(self, quInfo):
        self.infoBox.append("Video Information\n")
        self.infoBox.append("name: {}\nbvid: {}\n".format(
            quInfo[0]['title'], quInfo[0]['bvid']))

    def createWordcloud(self):
        link = self.linkEdit.text()
        wdcloud = VideoCommentWordCloud(getHeaders(True), "./download/wordcloud", "./api.cfg")
        #info_dict = wdcloud.get_wordcloud(link = link)

        th = threading.Thread(
            target=self.createThread, args=(wdcloud, link,))
        th.start()
        '''self.parentLyr.rightLogBox.addLog(
            "start to create wordcloud {}".format(info_dict['bvid']), "green"
        )'''
        self.parentLyr.rightLogBox.addLog(
            "please wait for seconds...", "green"
        )
    def createThread(self, wdcloud, link):
        wdcloud.set_font_path('../data/font/simhei.ttf')
        wdcloud.get_wordcloud(
            link
        )

        print("finish")
        self.parentLyr.rightLogBox.addLog(
            "creating finished",  "green"
        )
    def openDownloadFolder(self):
        self.getDownloadPath()
        os.startfile(self.downloadFolder)

    def getDownloadPath(self):
        self.downloadFolder = os.path.join(
            os.path.abspath(os.path.dirname(sys.argv[0])),
            "./download/wordcloud")
    def clearAll(self):
        self.linkEdit.clear()
        self.infoBox.clear()

'''class RightAnimationPreview(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)

        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStretch(0, 1)
        self.setLayout(layout)'''

class RightAnimationInfo(QtWidgets.QLabel):
    infoSignal = QtCore.pyqtSignal(list)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        #self.infoSignal.connect(self.updateQuInfo)

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)

        # info
        '''self.infoBox = QtWidgets.QTableWidget(0, 1, self)
        self.infoBox.verticalHeader().setVisible(False)
        self.infoBox.horizontalHeader().setVisible(False)
        self.downloadTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.downloadTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.infoBox.setFont(QtGui.QFont("Microsoft YaHei"))'''

        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(self.infoBox)
        layout.setStretch(0, 9)
        self.setLayout(layout)

    # def checkRank(self):
        
    '''def addDownload(self, info_dict):
        num = self.downloadTable.rowCount()
        self.downloadTable.setRowCount(num + 1)
        self.downloadTable.setRowHeight(num, 80)
        obj = SingleDownloadBox(self, info_dict)
        self.downloadTable.setCellWidget(num, 0, obj)

        self.update()
        return obj'''

'''class SingleDownloadBox(QtWidgets.QLabel):
    signal = QtCore.pyqtSignal(float)
    def __init__(self, _parent, info_dict):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.info_dict = info_dict
        self.initUI(info_dict)
        self.d_head = 0
        self.d_thread = None
        self.status = None
        self.signal.connect(self.updateBar)
'''

class RightLiveBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # set layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStretch(0, 1)
        self.setLayout(layout)

class RightLogBox(QtWidgets.QTextBrowser):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        self.setText(self.getDataTime()+\
            getColorText("Wellcome To Bilibili ToolBox\n", "black")
        )
        self.setFont(QtGui.QFont("Microsoft YaHei"))

    def getDataTime(self, f=True):
        # f: with format and color(blue)
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        out = getColorText("[%s]  "%currentTime, 'blue') if f else currentTime
        return out

    def addLog(self, info, color):
        dt = self.getDataTime()
        text = dt + getColorText(info+"\n", color)
        self.append(text)

    def clearAll(self):
        self.setText("")
# ------------------------------------------------------ #


# -------------- LEFT FUNCTIONAL BOX ------------------- #
class LeftFuncBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        # user information box
        self.userInfoBox = UserInfoBox(self)
        # download buttons
        self.downloadBtns = LeftDownloadBtns(self)
        # wordcloud buttons
        self.wordcloudBtns = LeftWordcloudBtns(self)
        # animation buttons
        self.animationBtns = LeftAnimationBtns(self)
        # live buttons
        self.liveBtns = LeftLiveBtns(self)
        # blank
        self.blankFilledBox = BlankFilledBox(self)
        # setting/folder
        self.settingFolderBox = SettingFolderBox(self)
        # add layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.userInfoBox, 0)
        layout.addWidget(self.downloadBtns, 1)
        layout.addWidget(self.wordcloudBtns, 2)
        layout.addWidget(self.animationBtns, 3)
        layout.addWidget(self.liveBtns, 4)
        layout.addWidget(self.settingFolderBox, 5)
        layout.setStretch(0, 4)
        layout.setStretch(1, 5)
        layout.setStretch(2, 5)
        layout.setStretch(3, 4)
        layout.setStretch(4, 4)
        layout.setStretch(5, 2)
        self.setLayout(layout)

class UserInfoBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.user_info = find(MainWindow, root).user_info
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # User Head Image
        img = Image.open(self.user_info['head']).resize((64, 64))
        img = ImageQt.toqpixmap(img)
        self.userHeadImg = QtWidgets.QLabel(self)
        self.userHeadImg.setGeometry(8, 8, 64, 64)
        self.userHeadImg.setPixmap(img)
        # User Name
        # bug: User Name may be too long!!!  
        self.userName = QtWidgets.QLabel(self)
        self.userName.setText(self.user_info['name'])
        self.userName.setGeometry(80, 10, 100, 20)
        self.userName.setFont(QtGui.QFont("Microsoft YaHei"))
        # User Gender
        self.userGender = QtWidgets.QLabel(self)
        self.userGender.setGeometry(110, 35, 15, 15)
        self.userGender.setPixmap(QtGui.QPixmap(self.getGender()))
        self.userGender.setScaledContents(True)
        # User Level
        self.userLevel = QtWidgets.QLabel(self)
        self.userLevel.setGeometry(80, 35, 25, 15)
        self.userLevel.setPixmap(QtGui.QPixmap(self.getLevel()))
        self.userLevel.setScaledContents(True)
        # User UID
        self.userUidPng = QtWidgets.QLabel(self)
        self.userUidPng.setGeometry(80, 55, 25, 15)
        self.userUidPng.setPixmap(QtGui.QPixmap("./data/resource/uid.png"))
        self.userUidPng.setScaledContents(True)
        self.userUidNum = QtWidgets.QLabel(self)
        self.userUidNum.setGeometry(110, 55, 80, 15)
        self.userUidNum.setText(self.user_info['uid'])
        self.userUidNum.setFont(QtGui.QFont("Microsoft YaHei"))

    def getGender(self):
        gender = self.user_info['gender']
        if gender == '男':
            return "./data/resource/male.png"
        elif gender == '女':
            return "./data/resource/female.png"
        else:
            return None

    def getLevel(self):
        level = self.user_info['level']
        return "./data/resource/level_%s.png"%str(level)

class LeftDownloadBtns(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.setGeometry(0, 0, 200, 40)
        self.videoFlag = False
        self.taskFlag = False

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # download label
        self.downloadNote = QtWidgets.QLabel(self)
        self.downloadNote.setText("download")
        self.downloadNote.setFont(QtGui.QFont("Microsoft YaHei"))
        self.downloadNote.setGeometry(20, 0, 160, 30)
        self.downloadNote.setAlignment(QtCore.Qt.AlignCenter)
        # Horizonal line
        self.hLine = QtWidgets.QFrame(self)
        self.hLine.setGeometry(20, 30, 160, 2)
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        # task button
        self.taskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/download.png"),
            "tasks",
            self)
        self.taskBtn.setGeometry(20, 35, 160, 30)
        self.taskBtn.setIconSize(QtCore.QSize(30, 30))
        self.taskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.taskBtn.setFlat(True)
        self.taskBtn.clicked.connect(self.flipToDownloadTask)
        # add task button
        self.addTaskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/add.png"),
            "new task",
            self)
        self.addTaskBtn.setGeometry(20, 65, 160, 30)
        self.addTaskBtn.setIconSize(QtCore.QSize(25, 25))
        self.addTaskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.addTaskBtn.setFlat(True)
        self.addTaskBtn.clicked.connect(self.flipToVideo)

    def flipToDownloadTask(self):
        if not self.taskFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("download")
            self.taskFlag = True
            self.videoFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.taskFlag = False

    def flipToVideo(self):
        if not self.videoFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("video")
            self.videoFlag = True
            self.taskFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.videoFlag = False
        
class LeftWordcloudBtns(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.setGeometry(0, 0, 200, 40)
        self.videoFlag = False
        self.taskFlag = False

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # wordcloud note
        self.wordcloudNote = QtWidgets.QLabel(self)
        self.wordcloudNote.setText("wordcloud")
        self.wordcloudNote.setFont(QtGui.QFont("Microsoft YaHei"))
        self.wordcloudNote.setGeometry(20, 0, 160, 30)
        self.wordcloudNote.setAlignment(QtCore.Qt.AlignCenter)
        #
        self.hLine = QtWidgets.QFrame(self)
        self.hLine.setGeometry(20, 30, 160, 2)
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        # task button
        '''self.taskBtn = QtWidgets.QPushButton(self)
        self.taskBtn.setGeometry(110, 5, 30, 30)
        self.taskBtn.setIcon(QtGui.QIcon("./data/resource/download.png"))
        self.taskBtn.setIconSize(QtCore.QSize(30, 30))
        self.taskBtn.setFlat(True)
        # self.taskBtn.clicked.connect(self.flipToDownloadTask)'''
        # preview button
        self.previewBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/bm_.png"),
            "preview",
            self)
        self.previewBtn.setGeometry(20, 35, 160, 30)
        self.previewBtn.setIconSize(QtCore.QSize(20, 20))
        self.previewBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.previewBtn.setFlat(True)
        self.previewBtn.clicked.connect(self.flipToPreview)
        # add task button
        self.addTaskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/add.png"),
            "new task",
            self)
        self.addTaskBtn.setGeometry(20, 65, 160, 30)
        self.addTaskBtn.setIconSize(QtCore.QSize(30, 30))
        self.addTaskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.addTaskBtn.setFlat(True)
        self.addTaskBtn.clicked.connect(self.flipToWordcloudCreate)

    def flipToPreview(self):
        if not self.taskFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("preview")
            self.taskFlag = True
            self.videoFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.taskFlag = False

    def flipToWordcloudCreate(self):
        if not self.videoFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("createwordcloud")
            self.videoFlag = True
            self.taskFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.videoFlag = False

class LeftAnimationBtns(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.setGeometry(0, 0, 200, 40)
        '''self.previewFlag = False
        self.taskFlag = False'''

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # wordcloud note
        self.wordcloudNote = QtWidgets.QLabel(self)
        self.wordcloudNote.setText("animation")
        self.wordcloudNote.setFont(QtGui.QFont("Microsoft YaHei"))
        self.wordcloudNote.setGeometry(20, 0, 160, 30)
        self.wordcloudNote.setAlignment(QtCore.Qt.AlignCenter)
        #
        self.hLine = QtWidgets.QFrame(self)
        self.hLine.setGeometry(20, 30, 160, 2)
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        # task button
        '''self.taskBtn = QtWidgets.QPushButton(self)
        self.taskBtn.setGeometry(110, 5, 30, 30)
        self.taskBtn.setIcon(QtGui.QIcon("./data/resource/download.png"))
        self.taskBtn.setIconSize(QtCore.QSize(30, 30))
        self.taskBtn.setFlat(True)
        # self.taskBtn.clicked.connect(self.flipToDownloadTask)'''
        # preview button
        '''self.previewBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/bm_.png"),
            "preview",
            self)
        self.previewBtn.setGeometry(20, 35, 160, 30)
        self.previewBtn.setIconSize(QtCore.QSize(20, 20))
        self.previewBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.previewBtn.setFlat(True)
        self.previewBtn.clicked.connect(self.flipToAnimationPreview)'''
        # add task button
        self.addTaskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/c3s.png"),
            "check rank",
            self)
        self.addTaskBtn.setGeometry(20, 40, 160, 30)
        self.addTaskBtn.setIconSize(QtCore.QSize(20, 20))
        self.addTaskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.addTaskBtn.setFlat(True)
        self.addTaskBtn.clicked.connect(self.flipToGetAnimationInfo)

    '''def flipToAnimationPreview(self):
        if not self.taskFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("animationinfopreview")
            self.taskFlag = True
            self.previewFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.taskFlag = False'''

    '''def flipToGetAnimationInfo(self):
        if not self.previewFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("animationinfocollect")
            self.previewFlag = True
            self.taskFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.previewFlag = False'''
    def flipToGetAnimationInfo(self):
        self.parentLyr.parentLyr.rightFuncBox.flipTabPage("animationinfocollect")

class LeftLiveBtns(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.setGeometry(0, 0, 200, 40)

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # wordcloud note
        self.wordcloudNote = QtWidgets.QLabel(self)
        self.wordcloudNote.setText("live show")
        self.wordcloudNote.setFont(QtGui.QFont("Microsoft YaHei"))
        self.wordcloudNote.setGeometry(20, 0, 160, 30)
        self.wordcloudNote.setAlignment(QtCore.Qt.AlignCenter)
        #
        self.hLine = QtWidgets.QFrame(self)
        self.hLine.setGeometry(20, 30, 160, 2)
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)

        # add task button
        self.addTaskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/bju.png"),
            "barrage",
            self)
        self.addTaskBtn.setGeometry(20, 40, 160, 30)
        self.addTaskBtn.setIconSize(QtCore.QSize(30, 30))
        self.addTaskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.addTaskBtn.setFlat(True)
        self.addTaskBtn.clicked.connect(self.flipToDealLive)

    def flipToDealLive(self):
        self.parentLyr.parentLyr.rightFuncBox.flipTabPage("live")

class BlankFilledBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)

class SettingFolderBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.downloadFolder = ""
        self.settingWflag = False
        self.moreWflag = False
        self.initUI()

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # Setting Btn
        self.settingBtn = QtWidgets.QPushButton(self)
        self.settingBtn.setIcon(QtGui.QIcon("./data/resource/setting.png"))
        self.settingBtn.setGeometry(5, 5, 30, 30)
        self.settingBtn.setIconSize(QtCore.QSize(30, 30))
        self.settingBtn.setFlat(True)
        self.settingBtn.clicked.connect(self.openSettingWindow)
        # Download Folder
        self.dlFolderBtn = QtWidgets.QPushButton(self)
        self.dlFolderBtn.setIcon(QtGui.QIcon("./data/resource/d_folder.png"))
        self.dlFolderBtn.setGeometry(40, 5, 30, 30)
        self.dlFolderBtn.setIconSize(QtCore.QSize(30, 30))
        self.dlFolderBtn.setFlat(True)
        self.dlFolderBtn.clicked.connect(self.openDownloadFolder)
        # More Btn
        self.moreBtn = QtWidgets.QPushButton(self)
        self.moreBtn.setIcon(QtGui.QIcon("./data/resource/more.png"))
        self.moreBtn.setGeometry(165, 5, 30, 30)
        self.moreBtn.setIconSize(QtCore.QSize(30, 30))
        self.moreBtn.setFlat(True)
        self.moreBtn.clicked.connect(self.openMoreWindow)
        # Setting Window
        self.settingWindow = SettingWindow(self)
        # More Window
        self.moreWindow = MoreWindow(self)

    def openDownloadFolder(self):
        self.getDownloadPath()
        os.startfile(self.downloadFolder)

    def getDownloadPath(self):
        self.downloadFolder = os.path.join(
            os.path.abspath(os.path.dirname(sys.argv[0])),
            "./download")

    def openSettingWindow(self):
        if not self.settingWflag:
            self.settingWindow.show()
            self.settingWflag = True
        else:
            self.settingWindow.close()

    def openMoreWindow(self):
        if not self.moreWflag:
            self.moreWindow.show()
            self.moreWflag = True
        else:
            self.moreWindow.close()

class SettingWindow(QtWidgets.QWidget):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(320, 480)
        self.setWindowTitle("Setting")
        self.setWindowIcon(QtGui.QIcon("./data/resource/setting.png"))

    def closeEvent(self, event):
        event.accept()
        self.parentLyr.settingWflag = False

class MoreWindow(QtWidgets.QWidget):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.info = {
            "version": "v1.0.0",
            "author": "Yijie Li\n"+\
                "                "+"Yongfei Yan\n"+\
                "                "+"Kaiwen Gong\n"+\
                "                "+"Lingfei Zhao\n"+\
                "                "+"Qiyu Li"
        }
        self.initUI()

    def initUI(self):
        self.setFixedSize(320, 380)
        self.setWindowTitle("More")
        self.setWindowIcon(QtGui.QIcon("./data/resource/more.png"))
        # Big Title
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setGeometry(20, 20, 280, 50)
        self.titleLabel.setText("Bilibili ToolBox")
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setFont(QtGui.QFont("Microsoft YaHei", 15, QtGui.QFont.Bold))
        # Version
        self.versionLabel = QtWidgets.QLabel(self)
        self.versionLabel.setGeometry(20, 100, 280, 20)
        self.versionLabel.setText("version:   %s"%self.info['version'])
        self.versionLabel.setFont(QtGui.QFont("Microsoft YaHei", 10, QtGui.QFont.Bold))
        # Author
        self.authorLabel = QtWidgets.QLabel(self)
        self.authorLabel.setGeometry(20, 130, 280, 120)
        self.authorLabel.setText("author:   %s"%self.info['author'])
        self.authorLabel.setFont(QtGui.QFont("Microsoft YaHei", 10, QtGui.QFont.Bold))
        # login btn
        self.loginBtn = QtWidgets.QPushButton(self)
        self.loginBtn.setGeometry(200, 320, 100, 30)
        self.loginBtn.setText("login")
        self.loginBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.loginBtn.clicked.connect(self.openLoginWindow)

    def closeEvent(self, event):
        event.accept()
        self.parentLyr.moreWflag = False

    def openLoginWindow(self):
        root.login()
        root.show()
        find(MainWindow, root).setVisible(False)
        self.close()
# ------------------------------------------------------ #


if __name__ == "__main__":
    # change to the path with this file
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # --maybe not work-- #
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # ------------------ #

    app = QtWidgets.QApplication(sys.argv)

    loginWindow = LoginWindow()
    sys.exit(app.exec_())