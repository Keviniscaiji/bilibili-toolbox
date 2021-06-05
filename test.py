class RightWordcloudCreate(QtWidgets.QLabel):
    infoSignal = QtCore.pyqtSignal(list)
    def __init__(self, _parent):
        super().__init__()
        self.childLyr = []
        self.parentLyr = _parent
        _parent.childLyr.append(self)
        self.downloadFolder = ""
        self.openSignal = 0
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

        self.linkEdit.setPlaceholderText('please enter the bvid')
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
        self.createBtn.setText("create wordcloud")
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
        self.openBtn = QtWidgets.QPushButton(self)
        self.openBtn.setGeometry(70, 320, 180, 30)
        self.openBtn.setText("open the folder")
        self.openBtn.setFont(QtGui.QFont("Microsoft YaHei"))
        self.openBtn.clicked.connect(self.openDownloadFolder)
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
        th = threading.Thread(target=self.infoThread, args=(link, ))
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

    '''def previewWC(self):
        signal = self.openSignal
        th = threading.Thread(traget=self.previewThread, args= (signal,))
        th.start()
    def previewThread(self, signal, link):
        if signal == 1:
            img = Image.open('./download/wordcloud/' + link + '_wc.png')
            plt.figure("test")
            plt.imshow(img)
            plt.show()
            signal = signal - 1'''

    def createWordcloud(self):
        link = self.linkEdit.text()
        wdcloud = VideoCommentWordCloud(getHeaders(True), "./download/wordcloud", "./api.cfg")
        #info_dict = wdcloud.get_wordcloud(link = link)
        th = threading.Thread(
            target=self.createThread, args=(wdcloud, link,))
        th.start()
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
        '''plt.imshow(wdcloud)
        plt.axis("off")
        plt.show()'''
        self.jumpToPreview()
    def jumpToPreview(self):
        lena = mpimg.imread('./download/wordcloud/BV16i4y1A7Ho_wc.png')
        plt.imshow(lena)
        plt.show()
        print("ok")

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