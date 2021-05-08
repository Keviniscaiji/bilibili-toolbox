from bilibili.Downloader import *
from bilibili.User import *

import os
import sys
import threading
import urllib
import time
import ctypes
import inspect
import json
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

# GUI utils
# Scroll Text
class ScrollTextLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(ScrollTextLabel, self).__init__(parent)
        self.txt = ""   
        self.newX = 0
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.changeTxtPosition)
        self.font = QtGui.QFont("Microsoft YaHei")

    def changeTxtPosition(self):
        if not self.parent().isVisible():
            self.t.stop()
            self.newX = 10
            return
        if self.textRect.width() + self.newX > 0:
            self.newX -= 5
        else:
            self.newX = self.width()            
        self.update()

    def setText(self, s):
        self.txt = s
        self.update()

    def enterEvent(self, event):
        self.t.start(150)

    def leaveEvent(self, event):
        self.t.stop()
        self.newX = 0
        self.update()

    def paintEvent(self, event):
        painter =  QtGui.QPainter(self)
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor('transparent'))

        self.textRect = painter.drawText(
            QtCore.QRect(0, -7, self.width(), 25), 
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.txt)

        if self.textRect.width() > self.width():
            painter.setPen(QtGui.QColor(0, 0, 0, 255))
            painter.drawText(
                QtCore.QRect(self.newX, -7, self.textRect.width(), 25), 
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.txt)
        else:
            painter.setPen(QtGui.QColor(0, 0, 0, 255))
            self.textRect = painter.drawText(
                QtCore.QRect(0, -7, self.width(), 25), 
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.txt)
            self.t.stop()

def saveAllState():
    history = find(RightHistoryBox, root).history
    with open('./download/history.json','w') as file_obj:
        json.dump(history, file_obj)

def loadAllState():
    # load history state
    with open('./download/history.json') as file_obj:
        history = json.load(file_obj)
    find(RightHistoryBox, root).setPreviousHistory(history)
    # load download state
    for cache_name in os.listdir('./download/video'):
        pass
        
def getDateTime():
    currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return currentTime
# ------------------------------------------------------ #


# -------------------- LOGIN WINDOW -------------------- #
class LoginWindow(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal(bool)
    signal2 = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        # init root layer #
        global root
        root = self
        self.loginMode = 'QRcode'
        self.emptyCookie = True
        self.qrcodeTimeout = False
        # --------------- #
        self.childLyr = []
        self.parentLyr = None
        self.mainWindow = None
        self.initUI()
        self.signal.connect(self.moveToMainWindow)
        self.signal2.connect(self.qrcodeTimeoutNotice)
        self.login()
        self.show()

    def initUI(self):
        self.setFixedSize(320, 400)
        self.setWindowTitle("Login")
        self.setWindowIcon(QtGui.QIcon("./data/resource/main.png"))
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
        # swap account login
        self.swapBtn = QtWidgets.QPushButton(self)
        self.swapBtn.setIcon(QtGui.QIcon("./data/resource/swap.png"))
        self.swapBtn.setGeometry(280, 10, 30, 30)
        self.swapBtn.setIconSize(QtCore.QSize(30, 30))
        self.swapBtn.setFlat(True)
        self.swapBtn.clicked.connect(self.swapLoginMode)

    def moveToMainWindow(self):
        try:
            stop_thread(self.th)
        except:
            pass
        self.qrcodeTimeout = False
        headers = getHeaders(True)
        user = BilibiliUser(headers, "./api.cfg")
        info = user.get_account_info()
        if info is not None:
            self.emptyCookie = False
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
        else:
            self.qrcodeTimeout = True
            self.signal2.emit(False)
    
    def login(self):
        cookieF = open("./cookie.txt", "r")
        if str(cookieF.readline()).strip('\n') == "":
            self.emptyCookie = True
            self.loginWithQRcode()
            self.loginMode = "QRcode"
            cookieF.close()
        else:
            self.emptyCookie = False
            self.loginWithCacheCookie()
            self.loginMode = "cookie"
            cookieF.close()

    def closeEvent(self, event):
        event.accept()
        os._exit(0)

    def loginWithQRcode(self):
        self.loginNotice.setText("Please login in 120 second")
        login_obj, qrcode_dict = self.getLoginQRcode()
        self.skipBtn.setText("skip")
        cookieF = open("./cookie.txt", "w")
        cookieF.write("")
        cookieF.close()
        self.emptyCookie = True
        self.th = threading.Thread(target=self.checkLogin, args=(login_obj, qrcode_dict,))
        self.th.start()

    def loginWithCacheCookie(self):
        if os.path.exists('./data/user/head.jpg'):
            img = Image.open('./data/user/head.jpg').resize((200, 200))
        else:
            img = Image.open('./data/resource/login.png').resize((200, 200))
        img = ImageQt.toqpixmap(img)
        self.qrCodeImage.setPixmap(img)
        self.loginNotice.setText("Cookie found, please login")
        self.skipBtn.setText("login")

    def swapLoginMode(self):
        if self.qrcodeTimeout:
            self.loginWithQRcode()
        else:
            if self.loginMode == "cookie":
                self.loginWithQRcode()
                self.loginMode = "QRcode"
            else:
                if not self.emptyCookie:
                    try:
                        stop_thread(self.th)
                    except:
                        pass
                    self.loginWithCacheCookie()
                    self.loginMode = "cookie"

    def qrcodeTimeoutNotice(self):
        self.loginNotice.setText("time exceed, please refresh")
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
        try:
            loadAllState()
        except:
            pass

    def initUI(self):
        self.setFixedSize(720, 480)
        self.setWindowTitle("Bilibili ToolBox")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QtGui.QIcon("./data/resource/main.png"))
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

    def viewAsTray(self):
        self.hide()
        self.SysTrayIcon = QtWidgets.QSystemTrayIcon(self)
        self.SysTrayIcon.setIcon(QtGui.QIcon('./data/resource/main.png'))
        self.SysTrayIcon.setToolTip("Bilibili Downloader")
        self.tray_menu = QtWidgets.QMenu(QtWidgets.QApplication.desktop())
        self.RestoreAction = QtWidgets.QAction(u'restore ', self, triggered=self.restoreMainWindow)
        self.QuitAction = QtWidgets.QAction(u'quit ', self, triggered=app.quit)
        self.tray_menu.addAction(self.RestoreAction)
        self.tray_menu.addAction(self.QuitAction)
        self.SysTrayIcon.setContextMenu(self.tray_menu)
        self.SysTrayIcon.show()

    def restoreMainWindow(self):
        self.show()
        self.SysTrayIcon.hide()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            'Quit',
            "Are you sure to quit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            saveAllState()
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
        self.rightOperationBox.addTab(RightHistoryBox(self), "history") # 3
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
        elif name == "history":
            self.rightOperationBox.setCurrentIndex(3)
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
    downloadSignal = QtCore.pyqtSignal(dict)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.initUI()
        self.qu_dict = {
            '4K 超清': 120,
            '1080P 高码率': 112,
            '1080P 高清': 80,
            '720P 60帧': 64,
            '720P 高清': 64,
            '480P 清晰': 32,
            '360P 流畅': 16,
            '240P 极速': 6,
            'cover': 'cover'
        }
        self.qu_user = None
        self.cids = {}
        self.selectedAllStatus = False
        self.infoSignal.connect(self.updateQuInfo)
        self.downloadSignal.connect(self.downloadStart)

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
        # search
        self.searchBtn = QtWidgets.QPushButton(self)
        self.searchBtn.setGeometry(380, 50, 100, 30)
        self.searchBtn.setText("search")
        self.searchBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.searchBtn.clicked.connect(self.searchVideoInfo)
        # video table
        self.videoTable = QtWidgets.QTableWidget(0, 1, self)
        self.videoTable.setGeometry(20, 100, 460, 200)
        self.videoTable.verticalHeader().setVisible(False)
        self.videoTable.horizontalHeader().setVisible(False)
        self.videoTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.videoTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
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
        # select all button
        self.selectAllBtn = QtWidgets.QPushButton(self)
        self.selectAllBtn.setIcon(QtGui.QIcon("./data/resource/unselected.png"))
        self.selectAllBtn.setGeometry(20, 325, 20, 20)
        self.selectAllBtn.setIconSize(QtCore.QSize(20, 20))
        self.selectAllBtn.setFlat(True)
        self.selectAllBtn.clicked.connect(self.selectAllVideo)
        # select all note
        self.selectAllLabel = QtWidgets.QLabel(self)
        self.selectAllLabel.setText("select all")
        self.selectAllLabel.setFont(QtGui.QFont("Microsoft YaHei"))
        self.selectAllLabel.setGeometry(50, 325, 80, 20)

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
    
    def addVideoBox(self, info):
        num = self.videoTable.rowCount()
        self.videoTable.setRowCount(num+1)
        self.videoTable.setRowHeight(num, 30)
        obj = SingleVideoBox(self, info)
        self.videoTable.setCellWidget(num, 0, obj)
        self.update()
        return obj

    def updateQuInfo(self, quInfo):
        self.qualityBox.clear()
        for item in quInfo[1]:
            self.qualityBox.addItem(item[0])
        self.qualityBox.addItem('cover')
        infos = quInfo[0]
        for i, item in enumerate(infos['data']['pages']):
            info = {
                'idx': i+1,
                'title': item['part'], 
                'cid': item['cid'], 
                'duration': item['duration']}
            self.addVideoBox(info)
            self.cids['cid'] = {'idx':i+1, 'title': item['part']}

    def download(self):
        link = self.linkEdit.text()
        if self.qu_user == 'cover':
            obj = find(RightDownloadBox, root).addDownload()
            th = threading.Thread(
                target=self.downloadThread, args=(obj, link, -2, "",))
            obj.d_thread = th
            th.start()
        else:
            for item in self.childLyr:
                if isinstance(item, SingleVideoBox):
                    if item.selected:
                        obj = find(RightDownloadBox, root).addDownload()
                        th = threading.Thread(
                            target=self.downloadThread, args=(
                                obj, link, item.info['idx'], item.info['title'], ))
                        obj.d_thread = th
                        th.start()
        
    def downloadThread(self, obj, link, piece_idx, piece_title):
        if self.qu_user != 'cover':
            downloader = VideoDownloader(getHeaders(True), "./download/video", "./api.cfg")
            obj.downloader = downloader
            info_dict = downloader.get_video_info(link=link)
            info = info_dict['data']
            info['d_type'] = 'video'
            info['p_idx'] = piece_idx
            info['p_title'] = piece_title
            self.downloadSignal.emit({'obj':obj, 'info_dict':info})
            qu = 32 if self.qu_user is None else self.qu_user
            res = downloader.operate_download_cache(bvid=info['bvid'], quality_param=qu, 
                                    piece_idx=piece_idx, title=piece_title, mode='n')
            status = downloader.download(
                info_dict, str(self.qu_user), piece_idx-1, callback=obj._progress)
        else:
            downloader = CoverDownloader(getHeaders(True), "./download/image", "./api.cfg")
            info_dict = downloader.get_video_info(link=link)
            info = info_dict['data']
            info['d_type'] = 'cover'
            self.downloadSignal.emit({'obj':obj, 'info_dict':info})
            downloader.download_Cover(
                info,
                obj._progress
            )

    def downloadStart(self, downloadInfo):
        info = downloadInfo['info_dict']
        downloadInfo['obj'].setDownloadInfo(info)
        if self.qu_user != 'cover':
            self.parentLyr.rightLogBox.addLog(
                "start to download P{} of video {}".format(
                    info['p_idx'], info['bvid']), "green")
        else:
            self.parentLyr.rightLogBox.addLog(
                "start to download cover of {}".format(info['bvid']), "green")

    def clearAll(self):
        self.qu_user = None
        self.qualityBox.clear()
        self.qualityBox.addItem("none")
        self.linkEdit.clear()
        self.videoTable.clearContents()
        self.videoTable.setRowCount(0)
        self.cids.clear()
        needRm = []
        for item in self.childLyr:
            if isinstance(item, SingleVideoBox):
                needRm.append(item)
        for item in needRm:
            self.childLyr.remove(item)
        self.selectAllBtn.setIcon(QtGui.QIcon("./data/resource/unselected.png"))
        self.selectedAllStatus = False

    def selectAllVideo(self):
        if self.selectedAllStatus:
            self.selectAllBtn.setIcon(QtGui.QIcon("./data/resource/unselected.png"))
            self.selectedAllStatus = False
            for item in self.childLyr:
                if isinstance(item, SingleVideoBox):
                    item.selected = True
                    item.swapSelectStatus()
        else:
            self.selectAllBtn.setIcon(QtGui.QIcon("./data/resource/selected.png"))
            self.selectedAllStatus = True
            for item in self.childLyr:
                if isinstance(item, SingleVideoBox):
                    item.selected = False
                    item.swapSelectStatus()
                
class SingleVideoBox(QtWidgets.QLabel):
    signal = QtCore.pyqtSignal(float)
    def __init__(self, _parent, info):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.info = info
        self.initUI()
        self.selected = False

    def initUI(self):
        # page index
        self.page = QtWidgets.QLabel(self)
        self.page.setText("P%d"%self.info['idx'])
        self.page.setFont(QtGui.QFont("Microsoft YaHei"))
        self.page.setGeometry(10, 5, 50, 20)
        # title
        self.title = ScrollTextLabel(self)
        self.title.setText(self.info['title'])
        self.title.setFont(QtGui.QFont("Microsoft YaHei"))
        self.title.setGeometry(60, 5, 300, 20)
        # select/unselect button
        self.selectBtn = QtWidgets.QPushButton(self)
        self.selectBtn.setIcon(QtGui.QIcon("./data/resource/unselected.png"))
        self.selectBtn.setGeometry(380, 5, 20, 20)
        self.selectBtn.setIconSize(QtCore.QSize(20, 20))
        self.selectBtn.setFlat(True)
        self.selectBtn.clicked.connect(self.swapSelectStatus)

    def swapSelectStatus(self):
        if self.selected:
            self.selectBtn.setIcon(QtGui.QIcon("./data/resource/unselected.png"))
            self.selected = False
        else:
            self.selectBtn.setIcon(QtGui.QIcon("./data/resource/selected.png"))
            self.selected = True

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

    def addDownload(self):
        num = self.downloadTable.rowCount()
        self.downloadTable.setRowCount(num+1)
        self.downloadTable.setRowHeight(num, 80)
        obj = SingleDownloadBox(self)
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
        find(LeftDownloadBtns, root).taskBtn.setIcon(QtGui.QIcon("./data/resource/download2.png"))
    
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
        if d_type == 'video':
            path = './download/video'
        else:
            path = './download/image'
        history = {
                'time': getDateTime(),
                'path': path,
                'type': d_type
        }
        if info_dict['d_status']:
            history['status'] = 'finished'
            if d_type == 'video':
                self.parentLyr.parentLyr.rightLogBox.addLog(
                    "{} P{} of {} finished".format(
                        d_type, info_dict['p_idx'], info_dict['bvid']), "green")
                history['filename'] = "{}_{}_video.flv".format(
                    info_dict['bvid'], info_dict['p_idx'])
                history['title'] = info_dict['p_title']
                history['page'] = info_dict['p_idx']
            else:
                self.parentLyr.parentLyr.rightLogBox.addLog(
                    "{} of {} finished".format(d_type, info_dict['bvid']), "green")
                history['filename'] = "{}_cover.png".format(info_dict['bvid'])
                history['title'] = info_dict['title']
                history['page'] = '-'
            self.tasksFinished += 1
        else:
            history['status'] = 'canceled'
            if d_type == 'video':
                self.parentLyr.parentLyr.rightLogBox.addLog(
                    "{} P{} of {} canceled".format(
                        d_type, info_dict['p_idx'], info_dict['bvid']), "red")
                history['filename'] = "{}_{}_video.flv".format(
                    info_dict['bvid'], info_dict['p_idx'])
                history['title'] = info_dict['p_title']
                history['page'] = info_dict['p_idx']
            else:
                self.parentLyr.parentLyr.rightLogBox.addLog(
                    "{} of {} canceled".format(d_type, info_dict['bvid']), "red")
                self.parentLyr.parentLyr.rightLogBox.addLog(
                    "{} of {} finished".format(d_type, info_dict['bvid']), "green")
                history['filename'] = "{}_cover.png".format(info_dict['bvid'])
                history['title'] = info_dict['title']
                history['page'] = '-'
            self.tasksNum -= 1
        if self.tasksFinished == self.tasksNum:
            self.resetHead()
            self.parentLyr.clearAll()
            find(LeftDownloadBtns, root).taskBtn.setIcon(QtGui.QIcon("./data/resource/download.png"))
        else:
            self.info.setText("Tasks:  {}/{}".format(
                self.tasksFinished, self.tasksNum))
        find(RightHistoryBox, root).addHistory(history)

class SingleDownloadBox(QtWidgets.QLabel):
    signal = QtCore.pyqtSignal(float)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.info_dict = None
        self.initUI()
        self.d_head = 0
        self.d_thread = None
        self.status = 'downloading'
        self.downloader = None
        self.signal.connect(self.updateBar)

    def initUI(self):
        # title
        self.title = ScrollTextLabel(self)
        self.title.setText("none")
        self.title.setGeometry(10, 10, 380, 20)
        # bvid
        self.bvid = QtWidgets.QLabel(self)
        self.bvid.setText("bvid:  none")
        self.bvid.setFont(QtGui.QFont("Microsoft YaHei"))
        self.bvid.setGeometry(10, 30, 200, 20)
        # page id
        self.pageId = QtWidgets.QLabel(self)
        self.pageId.setText("P none")
        self.pageId.setFont(QtGui.QFont("Microsoft YaHei"))
        self.pageId.setGeometry(210, 30, 60, 20)
        # status label
        self.statusLabel = QtWidgets.QLabel(self)
        self.statusLabel.setText("status: running")
        self.statusLabel.setFont(QtGui.QFont("Microsoft YaHei"))
        self.statusLabel.setGeometry(270, 30, 150, 20)
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
        # resume/pause btn
        self.resumeBtn = QtWidgets.QPushButton(self)
        self.resumeBtn.setGeometry(420, 30, 30, 30)
        self.resumeBtn.setIcon(QtGui.QIcon("./data/resource/pause.png"))
        self.resumeBtn.setFlat(True)
        self.resumeBtn.clicked.connect(self.resumePauseTask)
        # cancel btn
        self.cancelBtn = QtWidgets.QPushButton(self)
        self.cancelBtn.setGeometry(450, 30, 30, 30)
        self.cancelBtn.setIcon(QtGui.QIcon("./data/resource/cancel.png"))
        self.cancelBtn.setFlat(True)
        self.cancelBtn.clicked.connect(self.cancelTask)

    def setDownloadInfo(self, info_dict):
        self.info_dict = info_dict
        self.bvid.setText("bvid:  %s"%info_dict['bvid'])
        if info_dict['d_type'] == "video":
            self.pageId.setText("P%s"%str(info_dict['p_idx']))
            self.title.setText(info_dict['p_title'])
        else:
            self.pageId.setText("cover")
            self.title.setText(info_dict['title'])

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
            self.statusLabel.setText("status: finished")
            self.parentLyr.downloadHead.signal2.emit(self.info_dict)
            if self.info_dict['d_type'] == 'video':
                res = self.downloader.operate_download_cache(
                    bvid=self.info_dict['bvid'], 
                    quality_param=None, 
                    piece_idx=self.info_dict['p_idx'], mode='rm')
    
    def cancelTask(self):
        try:
            stop_thread(self.d_thread)
        except:
            pass
        self.info_dict['d_status'] = False
        self.statusLabel.setText("status: canceled")
        self.parentLyr.downloadHead.signal.emit(-self.bar.value())
        self.parentLyr.downloadHead.signal2.emit(self.info_dict)
        self.bar.setStyleSheet('''QProgressBar {   
            border: 1px solid grey;   
            border-radius: 5px;   
            text-align: center;
            background-color: #F8F8FF;}
            QProgressBar::chunk {   
                background-color: #FF0000;   }''')
        if self.info_dict['d_type'] == 'video':
            filename = "{}_{}_video.flv".format(self.info_dict['bvid'], self.info_dict['p_idx'])
            res = self.downloader.operate_download_cache(
                bvid=self.info_dict['bvid'], 
                quality_param=None, 
                piece_idx=self.info_dict['p_idx'], mode='rm')
            os.remove(os.path.join(self.downloader.path, filename))

    def resumePauseTask(self):
        if self.status == 'pause':
            self.resumeBtn.setIcon(QtGui.QIcon("./data/resource/pause.png"))
            self.statusLabel.setText("status: starting")
            if self.info_dict['d_type'] == 'video':
                th = threading.Thread(
                    target=self.downloadThread, args=(self._progress, ))
                self.d_thread = th
                th.start()
                self.status = 'downloading'
                self.statusLabel.setText("status: running")
        elif self.status == 'downloading':
            self.resumeBtn.setIcon(QtGui.QIcon("./data/resource/resume.png"))
            self.statusLabel.setText("status: paused")
            try:
                stop_thread(self.d_thread)
            except:
                pass
            self.status = 'pause'
        else:
            pass

    def downloadThread(self, callback):
        downloader = VideoDownloader(getHeaders(True), "./download/video")
        self.downloader = downloader
        info_dict = downloader.get_video_info(None, self.info_dict['bvid'])
        res = downloader.operate_download_cache(
            bvid=self.info_dict['bvid'], 
            quality_param=None, 
            piece_idx=self.info_dict['p_idx'], mode='r')
        status = downloader.download(
            info_dict, res['qu'], res['piece_idx']-1,
            callback=callback)

class RightHistoryBox(QtWidgets.QLabel):
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.history = []
        self.initUI()

    def initUI(self):
        # title
        self.historyTitle = QtWidgets.QLabel(self)
        self.historyTitle.setGeometry(0, 0, 520, 30)
        self.historyTitle.setText("Download History")
        self.historyTitle.setFont(QtGui.QFont("Microsoft YaHei"))
        self.historyTitle.setAlignment(QtCore.Qt.AlignCenter)
        # history table
        self.historyTab = QtWidgets.QTableWidget(0, 1, self)
        self.historyTab.setGeometry(10, 40, 500, 300)
        self.historyTab.verticalHeader().setVisible(False)
        self.historyTab.horizontalHeader().setVisible(False)
        self.historyTab.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.historyTab.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # clear history btn
        self.clearHistoryBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/clear.png"),
            "clear history",
            self)
        self.clearHistoryBtn.setGeometry(360, 345, 150, 25)
        self.clearHistoryBtn.setIconSize(QtCore.QSize(25, 25))
        self.clearHistoryBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.clearHistoryBtn.setFlat(True)
        self.clearHistoryBtn.clicked.connect(self.clearHistory)

    def addHistory(self, history):
        num = self.historyTab.rowCount()
        self.historyTab.setRowCount(num+1)
        self.historyTab.setRowHeight(num, 60)
        obj = SingleHistoryBox(self, history)
        if history['status'] == 'canceled':
            obj.pathBtn.setDisabled(True)
        self.historyTab.setCellWidget(num, 0, obj)
        self.update()
        if history not in self.history:
            self.history.append(history)

    def setPreviousHistory(self, historys):
        self.history = historys
        for item in historys:
            self.addHistory(item)

    def clearHistory(self):
        self.history = []
        self.historyTab.clearContents()
        self.historyTab.setRowCount(0)

class SingleHistoryBox(QtWidgets.QLabel):
    def __init__(self, parent, history):
        # history:
        # filename, path, title, type, page, status
        super().__init__(parent)
        self.history = history
        self.initUI()

    def initUI(self):
        # filename/time
        self.fileNameTimeLable = QtWidgets.QLabel(self)
        self.fileNameTimeLable.setGeometry(0, 0, 350, 20)
        self.fileNameTimeLable.setFont(QtGui.QFont("Microsoft YaHei"))
        self.fileNameTimeLable.setText("{}      {}".format(
            self.history['filename'], self.history['time']))
        # title
        self.titleLable = ScrollTextLabel(self)
        self.titleLable.setGeometry(0, 20, 350, 20)
        self.titleLable.setText(self.history['title'])
        # type/page/status
        self.typePageStatus = QtWidgets.QLabel(self)
        self.typePageStatus.setGeometry(0, 40, 300, 20)
        self.typePageStatus.setFont(QtGui.QFont("Microsoft YaHei"))
        self.typePageStatus.setText(
            "type: {}   page: {}   status: {}".format(
                self.history['type'],
                self.history['page'],
                self.history['status'])
        )
        # open file path button
        self.pathBtn = QtWidgets.QPushButton(self)
        self.pathBtn.setIcon(QtGui.QIcon("./data/resource/path.png"))
        self.pathBtn.setGeometry(400, 20, 35, 30)
        self.pathBtn.setIconSize(QtCore.QSize(35, 30))
        self.pathBtn.setFlat(True)
        self.pathBtn.clicked.connect(self.openFilePath)

    def openFilePath(self):
        path = os.path.join(
            os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "."), 
            self.history['path'].strip("./").replace("/", "\\"), 
            self.history['filename'])
        os.system("explorer /e,/select, {}".format(path))

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
        layout.addWidget(self.blankFilledBox, 2)
        layout.addWidget(self.settingFolderBox, 3)
        layout.setStretch(0, 4)
        layout.setStretch(1, 5)
        layout.setStretch(2, 13)
        layout.setStretch(3, 2)
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
        self.historyFlag = False
        self.taskFinishedFlag = True

    def initUI(self):
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        # download label
        self.downloadNote = QtWidgets.QLabel(self)
        self.downloadNote.setText("DOWNLOAD")
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
        self.taskBtn.setGeometry(20, 35, 80, 30)
        self.taskBtn.setIconSize(QtCore.QSize(30, 30))
        self.taskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.taskBtn.setFlat(True)
        self.taskBtn.clicked.connect(self.flipToDownloadTask)
        # add task button
        self.addTaskBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/add.png"),
            "new",
            self)
        self.addTaskBtn.setGeometry(100, 35, 80, 30)
        self.addTaskBtn.setIconSize(QtCore.QSize(25, 25))
        self.addTaskBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.addTaskBtn.setFlat(True)
        self.addTaskBtn.clicked.connect(self.flipToVideo)
        # history button
        self.historyBtn = QtWidgets.QPushButton(
            QtGui.QIcon("./data/resource/history.png"),
            "history",
            self)
        self.historyBtn.setGeometry(20, 65, 90, 30)
        self.historyBtn.setIconSize(QtCore.QSize(30, 30))
        self.historyBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.historyBtn.setFlat(True)
        self.historyBtn.clicked.connect(self.flipToHistory)

    def flipToDownloadTask(self):
        if not self.taskFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("download")
            self.taskFlag = True
            self.videoFlag = False
            self.historyFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.taskFlag = False

    def flipToVideo(self):
        if not self.videoFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("video")
            self.videoFlag = True
            self.taskFlag = False
            self.historyFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.videoFlag = False

    def flipToHistory(self):
        if not self.historyFlag:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("history")
            self.historyFlag = True
            self.taskFlag = False
            self.videoFlag = False
        else:
            self.parentLyr.parentLyr.rightFuncBox.flipTabPage("blank")
            self.historyFlag = False
        
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
        # To Tray Btn
        self.trayBtn = QtWidgets.QPushButton(self)
        self.trayBtn.setIcon(QtGui.QIcon("./data/resource/tray.png"))
        self.trayBtn.setGeometry(75, 5, 30, 30)
        self.trayBtn.setIconSize(QtCore.QSize(25, 25))
        self.trayBtn.setFlat(True)
        self.trayBtn.clicked.connect(self.toTray)
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

    def toTray(self):
        find(MainWindow, root).viewAsTray()

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
            "author": ""
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

    def closeEvent(self, event):
        event.accept()
        self.parentLyr.moreWflag = False
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