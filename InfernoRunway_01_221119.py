# Copyright (C) 2022 ENDOAI.
# 

import os
import sys
import time
from datetime import datetime

import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

"""Runway : Inferno AIOps Client for testing detection & diagnosis models"""

class Thread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.trained_file = None
        self.status = True
        self.cap = True

    def set_file(self, fname):
        # The data comes with the 'opencv-python' module
        self.trained_file = os.path.join(cv2.data.haarcascades, fname)

    def run(self):
        #self.cap = cv2.VideoCapture(0)
        self.cap = cv2.VideoCapture("C:\\SENA_DEV\\QT\\WIN_20221116_18_42_22_Pro.mp4")
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(length)
        cascade = cv2.CascadeClassifier(self.trained_file)
        while self.status:
            print("Fetching frame...")
            print(datetime. utcnow(). strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            ret, frame = self.cap.read()
            print(ret)
            print(datetime. utcnow(). strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            print("Frame fetched.")

            #h, w, ch = frame.shape
            #img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            #scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

            # Emit signal
            #self.updateFrame.emit(scaled_img)
            #continue
 
            if not ret:
                continue

            # Reading frame in gray scale to process the pattern
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detections = cascade.detectMultiScale(gray_frame, scaleFactor=1.1,
                                                  minNeighbors=5, minSize=(30, 30))

            # Drawing green rectangle around the pattern
            for (x, y, w, h) in detections:
                pos_ori = (x, y)
                pos_end = (x + w, y + h)
                color = (0, 255, 0)
                cv2.rectangle(frame, pos_ori, pos_end, color, 2)

            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img)
        sys.exit(-1)

class FrameProcessor(QTimer):
    updateFrame = Signal(QImage)
    def __init__(self, parent=None):
        QTimer.__init__(self, parent)
        self.timeout.connect(self.process)

        self.trained_file = None
        self.status = True

        self.cap = cv2.VideoCapture("C:\\SENA_DEV\\QT\\WIN_20221116_18_42_22_Pro.mp4")
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(length)

 
    def set_file(self, fname):
        # The data comes with the 'opencv-python' module
        self.trained_file = os.path.join(cv2.data.haarcascades, fname)
        self.cascade = cv2.CascadeClassifier(self.trained_file)
    
    def process(self):
        print(datetime. utcnow(). strftime('PROCESS @ %Y-%m-%d %H:%M:%S.%f')[:-3])
        # Reading frame in gray scale to process the pattern
        ret, frame = self.cap.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = self.cascade.detectMultiScale(gray_frame, scaleFactor=1.1,
                                                   minNeighbors=5, minSize=(30, 30))

        # Drawing green rectangle around the pattern
        for (x, y, w, h) in detections:
            pos_ori = (x, y)
            pos_end = (x + w, y + h)
            color = (0, 255, 0)
            cv2.rectangle(frame, pos_ori, pos_end, color, 2)

        # Reading the image in RGB to display it
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Creating and scaling QImage
        h, w, ch = color_frame.shape
        img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

        # Emit signal
        self.updateFrame.emit(scaled_img)
        return

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Inferno Runway")
        self.setGeometry(0, 0, 1024, 768)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        exit = QAction("Exit", self, triggered=qApp.quit)
        self.menu_file.addAction(exit)

        # Play menu
        play_menu = self.menuBar().addMenu("&Play")
        style = self.style()
        icon = QIcon.fromTheme("media-playback-start.png",
                               style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = tool_bar.addAction(icon, "Play")
        self._play_action.triggered.connect(self.start)
        play_menu.addAction(self._play_action)

        icon = QIcon.fromTheme("media-skip-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_action = tool_bar.addAction(icon, "Previous")
        #self._previous_action.triggered.connect(self.previous_clicked)
        #play_menu.addAction(self._previous_action)

        icon = QIcon.fromTheme("media-playback-pause.png",
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = tool_bar.addAction(icon, "Pause")
        #self._pause_action.triggered.connect(self._player.pause)
        #play_menu.addAction(self._pause_action)

        icon = QIcon.fromTheme("media-skip-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        self._next_action = tool_bar.addAction(icon, "Next")
        #self._next_action.triggered.connect(self.next_clicked)
        #play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme("media-frame-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_ArrowBack))
        self._next_action = tool_bar.addAction(icon, "BackwardFrame")
        #self._next_action.triggered.connect(self.next_clicked)
        #play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme("media-frame-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_ArrowForward))
        self._next_action = tool_bar.addAction(icon, "ForwardFrame")
        #self._next_action.triggered.connect(self.next_clicked)
        #play_menu.addAction(self._next_action)


        icon = QIcon.fromTheme("media-playback-stop.png",
                               style.standardIcon(QStyle.SP_MediaStop))
        self._stop_action = tool_bar.addAction(icon, "Stop")
        self._stop_action.triggered.connect(self.stop)
        play_menu.addAction(self._stop_action)

        #--------------------------------------------------------------------
        # Video Loop Play
        #
        tool_bar.addSeparator()

        verticalSeparator = QLabel() # blank label for spacing
        verticalSeparator.resize(1,1)
        tool_bar.addWidget(verticalSeparator)

        self.checkBoxToggleRepeat = QCheckBox('LOOP')
        tool_bar.addWidget(self.checkBoxToggleRepeat)
        self.checkBoxToggleRepeat.stateChanged.connect(self.toggleRepeat)
        #
        #--------------------------------------------------------------------

        # About
        self.menu_about = self.menu.addMenu("&About")
        about = QAction("About Qt", self, shortcut=QKeySequence(QKeySequence.HelpContents),
                        triggered=qApp.aboutQt)
        self.menu_about.addAction(about)

        # Create a label for the display camera
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        # Thread in charge of updating the image
        #self.th = Thread(self)
        #self.th.finished.connect(self.close)
        #self.th.updateFrame.connect(self.setImage)

        # FrameProcessor
        self.frameProcessor = FrameProcessor(self)
        self.frameProcessor.updateFrame.connect(self.setImage)

        # Model group
        self.group_model = QGroupBox("Trained model")
        self.group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        model_layout = QHBoxLayout()

        self.combobox = QComboBox()
        for xml_file in os.listdir(cv2.data.haarcascades):
            if xml_file.endswith(".xml"):
                self.combobox.addItem(xml_file)

        model_layout.addWidget(QLabel("File:"), 10)
        model_layout.addWidget(self.combobox, 90)
        self.group_model.setLayout(model_layout)


        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        right_layout = QHBoxLayout()
        right_layout.addWidget(self.group_model, 1)
        right_layout.addLayout(buttons_layout, 1)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(right_layout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connections
        #self.button1.clicked.connect(self.start)
        #self.button2.clicked.connect(self.kill_thread)
        #self.button2.clicked.connect(self.stop)
        self.button2.setEnabled(False)
        self.combobox.currentTextChanged.connect(self.set_model)

    @Slot()
    def toggleRepeat(self):
        print(self.checkBoxToggleRepeat.isChecked())

    @Slot()
    def set_model(self, text):
        #self.th.set_file(text)
        self.frameProcessor.set_file(text)

    @Slot()
    def kill_thread(self):
        print("Finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @Slot()
    def stop(self):
        print("Finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        #self.frameProcessor.cap.release()
        #cv2.destroyAllWindows()
        #self.status = False
        #self.th.terminate()
        # Give time for the thread to finish
        #time.sleep(1)
        self.frameProcessor.stop()

    @Slot()
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        #self.th.set_file(self.combobox.currentText())
        #self.th.start()
        self.frameProcessor.start(1)

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    app = QApplication()
    w = Window()
    w.show()
    sys.exit(app.exec())