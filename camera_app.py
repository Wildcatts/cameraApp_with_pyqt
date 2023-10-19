import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import cv2, imutils
import time
import datetime
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import numpy as np


from_class = uic.loadUiType("camera_app.ui")[0]

class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent=None) -> None:
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        while self.running == True:
            self.update.emit()
            time.sleep(0.05)

    def stop(self):
        self.running = False



class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("World Best Camera App")

        self.pixmap = QPixmap()

        # 변수 초기화
        self.isCameraOn = False
        self.isRecOn = False
        self.video_capture = None

        # 버튼 초기화
        self.rec_btn.hide()
        self.capture_btn.hide()


        # hsv 슬라이더 초기화
        self.hue_slider.setRange(-180, 180)  # 범위 설정: -180부터 180까지
        self.hue_slider.setSingleStep(1)  # 단계 설정: 1씩 증가/감소

        self.sat_slider.setRange(-100, 100)  # 범위 설정: -100부터 100까지
        self.sat_slider.setSingleStep(1)  

        self.value_slider.setRange(-100, 100)  
        self.value_slider.setSingleStep(1)

        # rgb 슬라이더 초기화
        self.red_slider.setRange(-255, 255)  # 범위 설정: -255부터 255까지
        self.red_slider.setSingleStep(1)  # 단계 설정: 1씩 증가/감소

        self.green_slider.setRange(-255, 255)
        self.green_slider.setSingleStep(1)

        self.blue_slider.setRange(-255, 255)
        self.blue_slider.setSingleStep(1)

        # 밝기 조절 슬라이드
        self.light_slider.setRange(-255, 255)
        self.light_slider.setSingleStep(1)

        # 스레드 인식
        self.camera = Camera(self)
        self.camera.daemon = True
        self.record = Camera(self)
        self.record.daemon = True


        # 파일 열기
        self.open_btn.clicked.connect(self.openFile)
        
        # 카메라 시작
        self.camera_btn.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)

        # 녹화 시작
        self.rec_btn.clicked.connect(self.clickRecord)
        self.record.update.connect(self.updateRecording)

        # 화면 캡쳐
        self.capture_btn.clicked.connect(self.capture)

        # HSV 슬라이더
        self.hue_slider.valueChanged.connect(self.change_hsv)
        self.sat_slider.valueChanged.connect(self.change_hsv)
        self.value_slider.valueChanged.connect(self.change_hsv)

        # RGB 슬라이더
        self.red_slider.valueChanged.connect(self.change_rgb)
        self.green_slider.valueChanged.connect(self.change_rgb)
        self.blue_slider.valueChanged.connect(self.change_rgb)

        # 밝기 조절 슬라이더
        self.light_slider.valueChanged.connect(self.change_light)

    def change_light(self):
        light = self.light_slider.value()

        lab_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)

        lab_image[:, :, 0] = np.clip(lab_image[:, :, 0] + light, 0, 255)

        rgb_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)

        q_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], rgb_image.strides[0], QImage.Format_RGB888)

        self.pixmap = QPixmap.fromImage(q_image)
        self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
        self.window.setPixmap(self.pixmap)

    def change_rgb(self):
        red = self.red_slider.value()
        green = self.green_slider.value()
        blue = self.blue_slider.value()

        bgr_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

        bgr_image[:, :, 0] = np.clip(bgr_image[:, :, 0] + blue, 0, 255)
        bgr_image[:, :, 1] = np.clip(bgr_image[:, :, 1] + green, 0, 255)
        bgr_image[:, :, 2] = np.clip(bgr_image[:, :, 2] + red, 0, 255)

        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], rgb_image.strides[0], QImage.Format_RGB888)

        self.pixmap = QPixmap.fromImage(q_image)
        self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
        self.window.setPixmap(self.pixmap)

    
    def change_hsv(self):
        hue = self.hue_slider.value()
        saturation = self.sat_slider.value()
        value = self.value_slider.value()

        hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)

        hsv_image[..., 0] = (hsv_image[..., 0] + hue) % 180
        hsv_image[..., 1] = np.clip(hsv_image[..., 1] + saturation, 0, 255)
        hsv_image[..., 2] = np.clip(hsv_image[..., 2] + value, 0, 255)
        bgr_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)

        q_image = QImage(bgr_image.data, bgr_image.shape[1], bgr_image.shape[0], bgr_image.strides[0], QImage.Format_RGB888)

        self.pixmap = QPixmap.fromImage(q_image)
        self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
        self.window.setPixmap(self.pixmap)


    def capture(self):
        self.now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        capturename = self.now + '.png'
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(capturename, self.image)

    def updateRecording(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        self.writer.write(self.image)

    def clickRecord(self):
        if self.isRecOn == False:
            self.rec_btn.setText('REC OFF')
            self.isRecOn = True

            self.recordingStart()
        else:
            self.rec_btn.setText('REC ON')
            self.isRecOn = False

            self.recordingStop()

    def recordingStart(self):
        self.record.running = True
        self.record.start()

        self.now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        videoname = self.now + '.avi'
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.writer = cv2.VideoWriter(videoname, self.fourcc, 20.0, (w, h))

    def recordingStop(self):
        self.record.running = False
        
        if self.isRecOn == True:
            self.writer.relese()


    def updateCamera(self):
        retal, image = self.video.read()
        if retal:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())

            self.window.setPixmap(self.pixmap)  
       

    def clickCamera(self):
        if self.isCameraOn == False:
            self.camera_btn.setText("Quit")
            self.isCameraOn = True
            self.rec_btn.show()
            self.capture_btn.show()

            self.cameraStart()
        else:
            self.camera_btn.setText("Connect")
            self.isCameraOn = False
            self.rec_btn.hide()
            self.capture_btn.hide()

            self.cameraStop()
            self.recordingStop()

    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    def cameraStop(self):
        self.camera.running = False
        self.video.release

    def openFile(self):
        file,_ = QFileDialog.getOpenFileName(filter='Image (*.*)')

        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")):
            self.image = cv2.imread(file)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            h, w, c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())

            self.window.setPixmap(self.pixmap)
        else:
            self.video_capture = cv2.VideoCapture(file)

            if self.video_capture.isOpened():
                while True:
                    ret, frame = self.video_capture.read()
                    
                    if not ret:
                        break
                    
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    height, width, _ = frame.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

                    self.pixmap = QPixmap.fromImage(q_image)
                    self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())

                    self.window.setPixmap(self.pixmap)
                    QApplication.processEvents()

                    time.sleep(0.05)  # 저장된 동영상에 맞게 setting

                self.video_capture.release()





if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())

    