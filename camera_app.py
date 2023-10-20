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
        self.isfilterOn = False
        self.video_capture = None

        # 버튼 숨기기
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
        self.playVideo = Camera(self)
        self.playVideo.daemon = True

        # 파일 열기
        self.open_btn.clicked.connect(self.openFile)
        
        # 동영상 재생
        self.playVideo.update.connect(self.updatePlay)

        # 카메라 시작
        self.camera_btn.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)
        self.camera.update.connect(self.change_image)

        # 녹화 시작
        self.rec_btn.clicked.connect(self.clickRecord)
        self.record.update.connect(self.updateRecording)
        self.record.update.connect(self.change_image)

        # 화면 캡쳐
        self.capture_btn.clicked.connect(self.capture)

        # HSV 슬라이더
        self.hue_slider.valueChanged.connect(self.change_image)
        self.sat_slider.valueChanged.connect(self.change_image)
        self.value_slider.valueChanged.connect(self.change_image)

        # RGB 슬라이더
        self.red_slider.valueChanged.connect(self.change_image)
        self.green_slider.valueChanged.connect(self.change_image)
        self.blue_slider.valueChanged.connect(self.change_image)

        # 밝기 조절 슬라이더
        self.light_slider.valueChanged.connect(self.change_image)

        # 동영상 필터 적용
        self.playVideo.update.connect(self.change_image)

        # 필터
        # self.sharpning_btn.clicked.connect(self.click_filter)
        # self.bilateral_btn.clicked.connect(self.click_filter)

    def click_filter(self):
        if self.isfilterOn == False:
            self.isCameraOn = True
            self.change_filter()
        else:
            self.isfilterOn = False
            self.image_filter = self.tmp

    def change_filter(self):
        ycrb_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2YCrCb)

        ycrb_image_b = ycrb_image[:, :, 0].astype(np.float32)
        blr_image = cv2.GaussianBlur(ycrb_image_b, (0, 0), 2.0)
        ycrb_image[:, :, 0] = np.clip(2. * ycrb_image_b - blr_image, 0, 255).astype(np.uint8)
        self.image_filter = cv2.cvtColor(ycrb_image, cv2.COLOR_YCrCb2RGB)

        q_image = QImage(self.image_filter.data, self.image_filter.shape[1], self.image_filter.shape[0], self.image_filter.strides[0], QImage.Format_RGB888)

        self.pixmap = QPixmap.fromImage(q_image)
        self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
        self.window.setPixmap(self.pixmap)

    def change_image(self):
        light = self.light_slider.value()

        red = self.red_slider.value()
        green = self.green_slider.value()
        blue = self.blue_slider.value()

        hue = self.hue_slider.value()
        saturation = self.sat_slider.value()
        value = self.value_slider.value()

        hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        hsv_image[..., 0] = (hsv_image[..., 0] + hue) % 180
        hsv_image[..., 1] = np.clip(hsv_image[..., 1] + saturation, 0, 255)
        hsv_image[..., 2] = np.clip(hsv_image[..., 2] + value, 0, 255)

        bgr_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        bgr_image[:, :, 0] = np.clip(bgr_image[:, :, 0] + blue, 0, 255)
        bgr_image[:, :, 1] = np.clip(bgr_image[:, :, 1] + green, 0, 255)
        bgr_image[:, :, 2] = np.clip(bgr_image[:, :, 2] + red, 0, 255)

        lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2Lab)
        lab_image[:, :, 0] = np.clip(lab_image[:, :, 0] + light, 0, 255)

        self.image = cv2.cvtColor(lab_image, cv2.COLOR_Lab2RGB)
        self.tmp  = self.image

        q_image = QImage(self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format_RGB888)

        self.pixmap = QPixmap.fromImage(q_image)
        self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
        self.window.setPixmap(self.pixmap)


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

    def playStart(self):
        self.playVideo.running = True
        self.playVideo.start()
        self.video = cv2.VideoCapture(self.file)
    
    def playStop(self):
        self.playVideo.running = False
        self.video.release

    def updatePlay(self):
        retval, image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)
            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())
            self.window.setPixmap(self.pixmap)
        else:
            self.playStop()

    def openFile(self):
        self.file,_ = QFileDialog.getOpenFileName(filter='Image (*.*)')

        if self.file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")):
            self.image = cv2.imread(self.file)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            h, w, c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.window.width(), self.window.height())

            self.window.setPixmap(self.pixmap)
        else:
            self.playStart()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())

    