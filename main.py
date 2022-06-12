from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSlider, QStyle, QComboBox, QVBoxLayout, QWidget, QStatusBar)
import sys,os
import cv2
from PIL import ImageQt,Image
class Thumbnailer(QWidget):

    def __init__(self, parent=None):
        super(Thumbnailer, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setFixedSize(1200,500)
        self.mp = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setWindowTitle("Thumbnailer 1.0")
        icon = QIcon("icon.png")
        self.setWindowIcon(icon)

        videoWidget = QVideoWidget()
        videoWidget.setStyleSheet("border:1px solid black")
        ob = QPushButton("Open Video")
        ob.setIconSize(QSize(20, 20))
        ob.setFont(QFont("Open Sans", 8))
        ob.clicked.connect(self.load)
        ob.setFixedHeight(24)

        self.array = []
        self.fileName = ""
        self.position = ""
        self.text = ""
        self.colorTone = "Normal"
        self.label = QLabel(self)
        self.label.setFixedWidth(600)
        self.label.setFixedHeight(400)
        self.label.setScaledContents(True)
        self.label.setStyleSheet("border: 1px solid black")

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(QSize(20, 20))
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        boxes = QVBoxLayout()
        boxes.setAlignment(Qt.AlignTop)
        boxes.setContentsMargins(0,150,0,0)

        self.cb = QComboBox(self)
        self.cb.addItems(["Normal", "Grayscale"])
        self.cb.setFixedWidth(80)
        self.cb.activated[str].connect(self.changeValue)

        self.changeButton = QPushButton()
        self.changeButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.changeButton.setFixedHeight(48)
        self.changeButton.setFixedWidth(80)
        self.changeButton.setEnabled(False)
        self.changeButton.clicked.connect(self.findImage)

        boxes.addWidget(self.changeButton)
        boxes.addWidget(self.cb)

        self.downloadButton = QPushButton(" Save Image")
        self.downloadButton.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        self.downloadButton.setFixedHeight(24)
        self.downloadButton.clicked.connect(self.download)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setFixedWidth(800)
        self.slider.sliderMoved.connect(self.setPosition)
        self.slider.sliderPressed.connect(self.mouse_up)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Open Sans", 7))
        self.statusBar.setFixedHeight(14)


        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(ob)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.slider)
        controlLayout.addWidget(self.downloadButton)

        topLayout = QHBoxLayout()
        topLayout.addWidget(videoWidget)
        topLayout.setContentsMargins(0, 0, 0, 0)
        topLayout.addLayout(boxes)
        topLayout.addWidget(self.label)


        layout = QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mp.setVideoOutput(videoWidget)
        self.mp.stateChanged.connect(self.mediaStateChanged)
        self.mp.positionChanged.connect(self.changed2)
        self.mp.durationChanged.connect(self.changed1)
        self.mp.error.connect(self.throwError)
        self.statusBar.showMessage("Ready")

    def changeValue(self):
        self.colorTone = self.cb.currentText()
        print(self.colorTone)
    def findImage(self):
        def getFrame(cap, sec):
            cap.set(cv2.CAP_PROP_POS_MSEC, sec)
            hasFrames, image = cap.read()
            if hasFrames:
                if self.colorTone == "Grayscale":
                    return ["result.jpg",cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) ,cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)]
                else:
                    return ["result.jpg", image, cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]
        cap = cv2.VideoCapture(self.fileName)
        self.array = getFrame(cap, self.position)
        i = Image.fromarray(self.array[2])
        image = ImageQt.ImageQt(i).copy()
        px = QPixmap.fromImage(image)
        self.label.setPixmap(px)
    def mouse_up(self):
        self.mp.play()
        self.mp.pause()
    def download(self):
        cv2.imwrite(os.getcwd()+"/"+self.array[0],self.array[1]);
        self.statusBar.showMessage("Saved successfully")
    def load(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select the video",".", "Video Files (*.mp4 *.flv *.mts *.avi)")
        if fileName != '':
            self.fileName =fileName
            self.mp.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.changeButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.play()
            self.mp.pause()

    def play(self):
        if self.mp.state() == QMediaPlayer.PlayingState:
            self.mp.pause()
        else:
            self.mp.play()

    def mediaStateChanged(self, state):
        if self.mp.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def changed2(self, position):
        self.position = position
        self.slider.setValue(position)

    def changed1(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mp.setPosition(position)

    def throwError(self):
        self.playButton.setEnabled(False)
        err = self.mp.errorString()
        self.statusBar.showMessage("Error: " + "Please update or load codec pack" if err == "" else err)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = Thumbnailer()
    player.show()
    sys.exit(app.exec_())