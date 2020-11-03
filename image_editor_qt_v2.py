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
    pixmap_brush: QtGui.QPixmap = None
    display_img: QtWidgets.QGraphicsPixmapItem = None
    display_mask: QtWidgets.QGraphicsPixmapItem = None
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
    brush_cursor: QtWidgets.QGraphicsPixmapItem = None
    painter: QtGui.QPainter = None
    painting: bool = False
    mask: QtGui.QBitmap = None
    # colors in BGRA
    global colors
    ##

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(924, 536)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
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
        self.controlPanel = QtWidgets.QGridLayout()
        self.controlPanel.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.controlPanel.setObjectName("controlPanel")
        self.labelBrushSizeValue = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelBrushSizeValue.sizePolicy().hasHeightForWidth())
        self.labelBrushSizeValue.setSizePolicy(sizePolicy)
        self.labelBrushSizeValue.setObjectName("labelBrushSizeValue")
        self.controlPanel.addWidget(self.labelBrushSizeValue, 1, 2, 1, 1)
        self.BrushSizeSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BrushSizeSlider.sizePolicy().hasHeightForWidth())
        self.BrushSizeSlider.setSizePolicy(sizePolicy)
        self.BrushSizeSlider.setMinimumSize(QtCore.QSize(0, 0))
        self.BrushSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.BrushSizeSlider.setObjectName("BrushSizeSlider")
        self.controlPanel.addWidget(self.BrushSizeSlider, 1, 1, 1, 1)
        self.labelBrushSize = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelBrushSize.sizePolicy().hasHeightForWidth())
        self.labelBrushSize.setSizePolicy(sizePolicy)
        self.labelBrushSize.setObjectName("labelBrushSize")
        self.controlPanel.addWidget(self.labelBrushSize, 1, 0, 1, 1)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider_2.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_2.setSizePolicy(sizePolicy)
        self.horizontalSlider_2.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.controlPanel.addWidget(self.horizontalSlider_2, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.controlPanel.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.controlPanel.addWidget(self.label_2, 2, 2, 1, 1)
        self.SideBar.addLayout(self.controlPanel)
        self.gridLayout.addLayout(self.SideBar, 0, 1, 2, 1)
        self.MainScreen = QtWidgets.QHBoxLayout()
        self.MainScreen.setObjectName("MainScreen")
        self.FuncBtn1 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn1.sizePolicy().hasHeightForWidth())
        self.FuncBtn1.setSizePolicy(sizePolicy)
        self.FuncBtn1.setMinimumSize(QtCore.QSize(100, 0))
        self.FuncBtn1.setObjectName("FuncBtn1")
        self.MainScreen.addWidget(self.FuncBtn1)
        self.FuncBtn2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn2.sizePolicy().hasHeightForWidth())
        self.FuncBtn2.setSizePolicy(sizePolicy)
        self.FuncBtn2.setMinimumSize(QtCore.QSize(100, 0))
        self.FuncBtn2.setObjectName("FuncBtn2")
        self.MainScreen.addWidget(self.FuncBtn2)
        self.FuncBtn3 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn3.sizePolicy().hasHeightForWidth())
        self.FuncBtn3.setSizePolicy(sizePolicy)
        self.FuncBtn3.setMinimumSize(QtCore.QSize(100, 0))
        self.FuncBtn3.setObjectName("FuncBtn3")
        self.MainScreen.addWidget(self.FuncBtn3)
        self.FuncBtn4 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn4.sizePolicy().hasHeightForWidth())
        self.FuncBtn4.setSizePolicy(sizePolicy)
        self.FuncBtn4.setMinimumSize(QtCore.QSize(100, 0))
        self.FuncBtn4.setObjectName("FuncBtn4")
        self.MainScreen.addWidget(self.FuncBtn4)
        self.gridLayout.addLayout(self.MainScreen, 1, 0, 1, 1)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setSizeIncrement(QtCore.QSize(0, 0))
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 924, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # add Image to GraphicsView
        # 產生繪圖場景
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # 連結 UI 功能
        self.FuncBtn1.clicked.connect(lambda: self.change_image(max(self.index - 1, 0)))
        self.FuncBtn2.clicked.connect(lambda: self.change_image(min(self.index + 1, len(self.image_list) - 1)))
        self.listWidget.itemSelectionChanged.connect(lambda: self.change_image(self.listWidget.currentRow()))
        self.BrushSizeSlider.valueChanged.connect(lambda:
                                                  self.labelBrushSizeValue.setText(str((self.BrushSizeSlider.value() + 1) / 10))
                                                  )
        self.BrushSizeSlider.sliderReleased.connect(self.change_brush_size)

        # 滑鼠事件
        self.graphicsView.mousePressEvent = self.paint_stroke
        self.graphicsView.mouseMoveEvent = self.mouse_movement
        self.graphicsView.mousePressEvent = self.start_paint
        self.graphicsView.mouseReleaseEvent = self.end_paint

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
        self.change_image(0)
        # 產生筆刷游標
        self.BrushSizeSlider.setValue(20)
        self.change_brush_size()
        ##

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelBrushSizeValue.setText(_translate("MainWindow", "00"))
        self.labelBrushSize.setText(_translate("MainWindow", "Brush Size"))
        self.label.setText(_translate("MainWindow", "TextLabel"))
        self.label_2.setText(_translate("MainWindow", "00"))
        self.FuncBtn1.setText(_translate("MainWindow", "<<"))
        self.FuncBtn2.setText(_translate("MainWindow", ">>"))
        self.FuncBtn3.setText(_translate("MainWindow", "Undo"))
        self.FuncBtn4.setText(_translate("MainWindow", "Redo"))

    # Custom Methods
    def key_event(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)

        if e.key() == QtCore.Qt.Key_Minus or e.key() == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)

    # 開始繪圖
    def start_paint(self, e):
        self.painting = True
        self.painter = QtGui.QPainter(self.pixmap_mask)
        self.painter.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        p = self.painter.pen()
        # p.setWidth(self.brush_size)
        # p.setColor(QtGui.QColor(249, 39, 253, 128))
        # p.setColor(QtGui.QColor(255, 255, 255, 255))
        p.setColor(QtGui.QColor(0, 0, 0, 0))
        self.painter.setPen(p)
        self.painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        t = self.graphicsView.viewportTransform()
        r = self.brush_size
        curr_x = int((e.x() - t.m31()) / self.img_scale) - int(r / 2)
        curr_y = int((e.y() - t.m32()) / self.img_scale) - int(r / 2)
        self.painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        self.painter.drawEllipse(curr_x, curr_y, r, r)
        self.centralwidget.update()
        self.update_mask()

    # 結束繪圖
    def end_paint(self, e):
        self.painting = False
        # self.update_mask()
        self.painter.end()

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e):
        t = self.graphicsView.viewportTransform()
        offset = int((self.brush_size * self.img_scale) / 2)
        if self.painting:
            r = self.brush_size
            curr_x = int((e.x() - t.m31()) / self.img_scale) - int(r / 2)
            curr_y = int((e.y() - t.m32()) / self.img_scale) - int(r / 2)
            self.painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            self.painter.drawEllipse(curr_x, curr_y, r, r)
            self.centralwidget.update()
            self.update_mask()

        self.statusbar.showMessage(f'x: {e.x()}, y: {e.y()}')
        self.brush_cursor.setPos(QtCore.QPoint(e.x() - offset - t.m31(), e.y() - offset - t.m32()))

    # 調整顯示大小
    def scale_display(self, value: int):
        image = self.display_img.pixmap()
        h, w = image.height(), image.width()
        image = self.pixmap_img.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.display_img.setPixmap(image)
        image = self.pixmap_mask.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.display_mask.setPixmap(image)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, image.width(), image.height()))
        self.img_scale = image.width() / self.pixmap_img.width()
        self.brush_cursor.setScale(self.img_scale)

    # 切換圖片
    def change_image(self, _index: int):
        if _index == self.index:
            return
        else:
            self.index = _index
            self.listWidget.setCurrentRow(_index)

        self.pixmap_img = QtGui.QPixmap(self.image_list[_index])
        img = self.pixmap_img.scaled(
            self.graphicsView.width(),
            self.graphicsView.height(),
            QtCore.Qt.KeepAspectRatio
        )

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(img)
        else:
            self.display_img.setPixmap(img)

        clayer = np.zeros([self.pixmap_img.height(), self.pixmap_img.width(), 4], dtype=np.uint8)
        clayer[:, :] = [249, 39, 253, 128]
        print(clayer)
        h, w, c = clayer.shape
        self.pixmap_mask = QtGui.QPixmap(QtGui.QImage(clayer, w, h, w * c, QtGui.QImage.Format_ARGB32))

        self.mask = QtGui.QBitmap(self.mask_list[_index])
        print(self.mask)
        self.pixmap_mask.setMask(self.mask)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, img.width(), img.height()))
        self.img_scale = img.width() / self.pixmap_img.width()
        # print(self.img_scale)

        self.update_mask()

    # 改變筆刷大小
    def change_brush_size(self):
        value = self.BrushSizeSlider.value()
        self.brush_size = int(5 * (value + 1))
        self.gen_brush()

    def paint_stroke(self, event):
        if self.mask_raw is not None:
            t = self.graphicsView.viewportTransform()
            x = int((event.x() - t.m31()) / self.img_scale)
            y = int((event.y() - t.m32()) / self.img_scale)
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

    def update_mask(self):
        # h, w, c = self.mask_raw.shape
        # res = QtGui.QImage(self.mask_raw, w, h, w * c, QtGui.QImage.Format_ARGB32)
        # self.pixmap_mask = QtGui.QPixmap(res)

        if self.display_mask is None:
            mask = self.pixmap_mask.scaled(
                self.graphicsView.width(),
                self.graphicsView.height(),
                QtCore.Qt.KeepAspectRatio
            )
            self.display_mask = self.scene.addPixmap(mask)
        else:
            mask = self.display_img.pixmap()
            h, w = mask.height(), mask.width()
            mask = self.pixmap_mask.scaled(w, h, QtCore.Qt.KeepAspectRatio)
            self.display_mask.setPixmap(mask)

    def gen_brush(self):
        if self.brush_cursor is not None:
            self.scene.removeItem(self.brush_cursor)
        pen = QtGui.QPen(QtCore.Qt.yellow)
        self.brush_cursor = self.scene.addEllipse(
            QtCore.QRectF(0, 0, self.brush_size, self.brush_size),
            pen,
            QtGui.QBrush(QtGui.QColor(255, 255, 0, 128))
        )
        self.brush_cursor.setScale(self.img_scale)
        # r = self.brush_size // 2
        # self.brush_raw = np.zeros((self.brush_size, self.brush_size, 4), np.uint8)
        # print(self.brush_raw.shape)
        # for i in range(-r, r):
        #     for j in range(-r, r):
        #         # print (r + i, r + j)
        #         if (i * i + j * j) <= (r * r):
        #             self.brush_raw[r + i][r + j] = colors.YELLOW
        #         else:
        #             self.brush_raw[r + i][r + j] = colors.BLANK
        #
        # img = QtGui.QImage(
        #     self.brush_raw,
        #     self.brush_size,
        #     self.brush_size,
        #     self.brush_size * 4,
        #     QtGui.QImage.Format_ARGB32
        # )
        # self.pixmap_brush = QtGui.QPixmap(img)
        # scale = int(self.img_scale * self.brush_size) * 10
        # display = self.pixmap_brush.scaled(scale, scale, QtCore.Qt.KeepAspectRatio)
        # if self.brush_cursor is None:
        #     self.brush_cursor = self.scene.addPixmap(display)
        # else:
        #     self.brush_cursor.setPixmap(display)
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
