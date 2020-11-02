# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_ui_v2.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import numpy as np
import skimage.io
from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets


@dataclass
class Colors:
    BLANK = (0, 0, 0, 0)
    PINK = (253, 39, 249, 128)
    YELLOW = (0, 255, 255, 128)
    WHITE = (255, 255, 255, 255)


class Ui_MainWindow(object):
    # Variables
    pixmap_img: QtGui.QPixmap = None
    pixmap_mask: QtGui.QPixmap = None
    scene: QtWidgets.QGraphicsScene = None
    zoom_scale = 100

    image_list = []
    mask_list = []
    image_dir = 'images'
    index = -1
    mask_raw: np.array = None
    img_scale = 1.0
    brush_size = 300
    brush_raw: np.array = None
    # colors in BGRA
    global colors

    ##

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(798, 536)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.Photo = QtWidgets.QLabel(self.centralwidget)
        self.Photo.setObjectName("Photo")
        self.gridLayout.addWidget(self.Photo, 0, 0, 1, 1)
        self.MaskImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.MaskImage.sizePolicy().hasHeightForWidth())
        self.MaskImage.setSizePolicy(sizePolicy)
        self.MaskImage.setObjectName("MaskImage")
        self.gridLayout.addWidget(self.MaskImage, 0, 0, 1, 1)
        self.SideBar = QtWidgets.QVBoxLayout()
        self.SideBar.setObjectName("SideBar")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QtCore.QSize(200, 0))
        self.listWidget.setObjectName("listWidget")
        self.SideBar.addWidget(self.listWidget)
        self.FuncBtn5 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn5.sizePolicy().hasHeightForWidth())
        self.FuncBtn5.setSizePolicy(sizePolicy)
        self.FuncBtn5.setMinimumSize(QtCore.QSize(200, 0))
        self.FuncBtn5.setObjectName("FuncBtn5")
        self.SideBar.addWidget(self.FuncBtn5)
        self.gridLayout.addLayout(self.SideBar, 0, 1, 4, 1)
        self.MainScreen = QtWidgets.QHBoxLayout()
        self.MainScreen.setObjectName("MainScreen")
        self.FuncBtn1 = QtWidgets.QPushButton(self.centralwidget)
        self.FuncBtn1.setObjectName("FuncBtn1")
        self.MainScreen.addWidget(self.FuncBtn1)
        self.FuncBtn2 = QtWidgets.QPushButton(self.centralwidget)
        self.FuncBtn2.setObjectName("FuncBtn2")
        self.MainScreen.addWidget(self.FuncBtn2)
        self.FuncBtn3 = QtWidgets.QPushButton(self.centralwidget)
        self.FuncBtn3.setObjectName("FuncBtn3")
        self.MainScreen.addWidget(self.FuncBtn3)
        self.FuncBtn4 = QtWidgets.QPushButton(self.centralwidget)
        self.FuncBtn4.setObjectName("FuncBtn4")
        self.MainScreen.addWidget(self.FuncBtn4)
        self.gridLayout.addLayout(self.MainScreen, 1, 0, 1, 1)
        self.BrushCursor = QtWidgets.QLabel(self.centralwidget)
        self.BrushCursor.setObjectName("BrushCursor")
        self.gridLayout.addWidget(self.BrushCursor, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 798, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # add Image to GraphicsView
        # 連結按鍵功能
        self.FuncBtn1.clicked.connect(lambda: self.change_image(False))
        self.FuncBtn2.clicked.connect(lambda: self.change_image(True))

        # 滑鼠事件
        self.MaskImage.setMouseTracking(True)
        self.MaskImage.mousePressEvent = self.paint_stroke
        self.MaskImage.mouseMoveEvent = self.stroke_cursor

        # 鍵盤事件
        MainWindow.keyPressEvent = self.key_event

        # 列出圖片檔名
        import os
        for file in os.listdir(self.image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(self.image_dir + '/' + file[: len(file) - 9] + '.JPG')
                self.mask_list.append(self.image_dir + '/' + file)

        self.listWidget.addItems(self.image_list)

        # 設定初始圖片
        self.change_image(True)
        # 產生筆刷游標
        self.gen_brush()
        ##

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.MaskImage.setText(_translate("MainWindow", "TextLabel"))
        self.Photo.setText(_translate("MainWindow", "TextLabel"))
        self.FuncBtn5.setText(_translate("MainWindow", "Select"))
        self.FuncBtn1.setText(_translate("MainWindow", "<<"))
        self.FuncBtn2.setText(_translate("MainWindow", ">>"))
        self.FuncBtn3.setText(_translate("MainWindow", "Undo"))
        self.FuncBtn4.setText(_translate("MainWindow", "Redo"))
        self.BrushCursor.setText(_translate("MainWindow", "TextLabel"))

    # Custom Methods
    def key_event(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)

        if e.key() == QtCore.Qt.Key_Minus or e.key() == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)

    def scale_display(self, value: int):

        h, w = self.Photo.height(), self.Photo.width()
        image = self.pixmap_img.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.Photo.setPixmap(image)
        image = self.pixmap_mask.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.MaskImage.setPixmap(image)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, image.width(), image.height()))
        self.img_scale = image.width() / self.mask_raw.shape[1]

    # 切換圖片
    def change_image(self, forward: bool):
        if forward:
            self.index = min(self.index + 1, len(self.image_list) - 1)
        else:
            self.index = max(self.index - 1, 0)

        self.pixmap_img = QtGui.QPixmap(self.image_list[self.index])
        img = self.pixmap_img.scaled(
            self.MaskImage.width(),
            self.MaskImage.height(),
            QtCore.Qt.KeepAspectRatio
        )
        self.Photo.setPixmap(img)

        mask = skimage.io.imread(self.mask_list[self.index])
        self.mask_raw = np.where(mask, colors.BLANK, colors.PINK).astype(np.uint8)

        self.img_scale = self.MaskImage.width() / self.mask_raw.shape[1]
        print(self.img_scale)
        self.update_mask()

    def paint_stroke(self, event):
        if self.mask_raw is not None:

            x = int(event.x() / self.img_scale)
            y = int(event.y() / self.img_scale)
            print(x, y)

            # for i in range(-100, 100):
            #     for j in range(-100, 100):
            #         self.mask_img[y + i][x + j] = (0, 0, 0, 0)

            r = self.brush_size // 2
            h, w, c = self.mask_raw.shape
            r_square = r * r
            for i in range(-r, r):
                i_square = i * i
                ycord = max(min((y + i), h - 1), 0)
                for j in range(-r, r):
                    if (i_square + j * j) <= r_square:
                        self.mask_raw[ycord][max(min((x + j), w - 1), 0)] = colors.BLANK
            self.update_mask()

        else:
            print('No mask loaded')

    def stroke_cursor(self, event):
        offset = int((self.brush_size * self.img_scale) / 2)
        # self.brush_cursor.moveBy(event.x() - offset + 6, event.y() - offset + 3)
        self.statusbar.showMessage(f'x: {event.x()}, y: {event.y()}')

    def update_mask(self):
        h, w, c = self.mask_raw.shape
        res = QtGui.QImage(self.mask_raw, w, h, w * c, QtGui.QImage.Format_ARGB32)
        self.pixmap_mask = QtGui.QPixmap(res)

        h, w = self.MaskImage.height(), self.MaskImage.width()
        mask = self.pixmap_mask.scaled(w, h, QtCore.Qt.KeepAspectRatio)
        self.MaskImage.setPixmap(mask)

    def gen_brush(self):
        para = int(self.brush_size * self.img_scale)
        print(para)
        r = para // 2
        self.brush_raw = np.zeros((para, para, 4), np.uint8)
        print(self.brush_raw.shape)
        for i in range(-r, r):
            for j in range(-r, r):
                # print (r + i, r + j)
                if (i * i + j * j) <= (r * r):
                    self.brush_raw[r + i][r + j] = colors.YELLOW
                else:
                    self.brush_raw[r + i][r + j] = colors.BLANK

        img = QtGui.QImage(self.brush_raw, para, para, para * 4, QtGui.QImage.Format_ARGB32)
        self.BrushCursor.setPixmap(QtGui.QPixmap(img))
    ##


if __name__ == "__main__":
    import sys
    colors = Colors()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
