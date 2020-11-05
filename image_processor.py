import os
import numpy as np
from dataclasses import dataclass
import configparser
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget, QStatusBar, QListWidget, \
    QSlider, QFileDialog, QDialog, QPushButton, QDoubleSpinBox
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QBrush, QImage, QPen
from PyQt5 import QtCore
from savedialog import Ui_SaveDialog
from deletedialog import Ui_DeleteDialog


@dataclass
class Colors:
    BLANK = QColor(0, 0, 0, 0)
    PINK = QColor(249, 39, 253, 128)
    YELLOW = QColor(255, 255, 0, 128)
    WHITE = QColor(255, 255, 255, 255)


class UIReferences:
    root: QWidget = None
    viewport: QGraphicsView = None
    statusbar: QStatusBar = None
    file_list_widget: QListWidget = None
    brush_size_slide: QSlider = None
    brush_size_dsb: QDoubleSpinBox = None
    prev_btn: QPushButton = None
    next_btn: QPushButton = None

    def __init__(self,
                 _root: QWidget,
                 _viewport: QGraphicsView,
                 _statusbar: QStatusBar,
                 _file_list_widget: QListWidget,
                 _brush_size_slide: QSlider,
                 _brush_size_dsb: QDoubleSpinBox,
                 _prev_btn: QPushButton,
                 _next_btn: QPushButton
                 ):
        self.root = _root
        self.viewport = _viewport
        self.statusbar = _statusbar
        self.file_list_widget = _file_list_widget
        self.brush_size_slide = _brush_size_slide
        self.brush_size_dsb = _brush_size_dsb
        self.prev_btn = _prev_btn
        self.next_btn = _next_btn


class ImageProcessor:
    #
    pixmap_img: QPixmap = None
    pixmap_mask: QPixmap = None
    pixmap_brush: QPixmap = None
    display_img: QGraphicsPixmapItem = None
    display_mask: QGraphicsPixmapItem = None
    scene: QGraphicsScene = None
    zoom_scale = 100
    # 檔案相關
    image_list = []
    mask_list = []
    image_dir = './'
    index = -1
    # 繪圖相關
    img_scale = 1.0
    brush_size = 300
    brush_cursor: QGraphicsPixmapItem = None
    painter: QPainter = None
    painting: bool = False
    erase_mode: bool = True
    mask: QBitmap = None
    colors = Colors()
    # 緩衝區相關
    pix_buffer = []
    buffer_idx: int = -1
    buffer_size: int = 50
    # 上層顯示物件
    ui: UIReferences = None
    # 設定檔解析器
    config: configparser = None

    def init(self):

        # 開啟設定檔
        try:
            settings = open("settings.ini", "r")
            settings.close()
            self.config = configparser.ConfigParser()
            self.config.read("settings.ini")
        except FileNotFoundError:
            self.getfile()
            self.config = configparser.ConfigParser()

            self.config["GeneralSettings"] = {'imagedir': self.image_dir,  # 圖片資料夾
                                              }
            self.config["WorkingState"] = {'workingimg': '0',
                                           'brushsize': '300',
                                           'erasemode': '1'
                                           }
            with open('settings.ini', 'w') as file:
                self.config.write(file)

        self.image_dir = self.config.get('GeneralSettings', 'imagedir')
        self.index = int(self.config.get('WorkingState', 'workingimg'))
        self.brush_size = int(self.config.get('WorkingState', 'brushsize'))
        self.erase_mode = bool(self.config.get('WorkingState', 'erasemode'))

        # 列出圖片檔名
        for file in os.listdir(self.image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(file[: len(file) - 9] + '.JPG')
                self.mask_list.append(file)

    def key_event(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)

        if e.key() == QtCore.Qt.Key_Minus or e.key() == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)

    # 開始繪圖
    def start_paint(self, e):
        self.painting = True
        self.painter = QPainter(self.pixmap_mask)
        self.painter.setCompositionMode(QPainter.CompositionMode_Plus)
        p = self.painter.pen()
        p.setColor(self.colors.PINK)
        self.painter.setPen(p)
        self.painter.setBrush(QBrush(self.colors.PINK))
        t = self.ui.viewport.viewportTransform()
        r = self.brush_size
        curr_x = int((e.x() - t.m31()) / self.img_scale) - int(r / 2)
        curr_y = int((e.y() - t.m32()) / self.img_scale) - int(r / 2)
        self.painter.setCompositionMode(
            QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
        )
        self.painter.drawEllipse(curr_x, curr_y, r, r)
        self.ui.root.update()
        self.update_mask()

    # 結束繪圖
    def end_paint(self, e):
        self.painting = False
        # self.update_mask()
        self.painter.end()
        self.update_buffer()

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e):
        t = self.ui.viewport.viewportTransform()
        offset = int((self.brush_size * self.img_scale) / 2)
        if self.painting:
            r = self.brush_size
            curr_x = int((e.x() - t.m31()) / self.img_scale) - int(r / 2)
            curr_y = int((e.y() - t.m32()) / self.img_scale) - int(r / 2)
            self.painter.setCompositionMode(
                QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
            )
            self.painter.drawEllipse(curr_x, curr_y, r, r)
            self.ui.root.update()
            self.update_mask()

        self.ui.statusbar.showMessage(f'x: {e.x()}, y: {e.y()}')
        self.brush_cursor.setPos(QtCore.QPoint(int(e.x() - offset - t.m31()), int(e.y() - offset - t.m32())))

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
        self.ui.prev_btn.setDisabled(True)
        self.ui.next_btn.setDisabled(True)
        if len(self.pix_buffer) > 1:
            sig = []
            save_dialog = QDialog()
            dui = Ui_SaveDialog(sig)
            dui.setupUi(save_dialog)
            save_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            save_dialog.exec()
            if sig[0] == 3:
                self.ui.prev_btn.setDisabled(False)
                self.ui.next_btn.setDisabled(False)
                return
            if sig[0] == 1:
                self.save_mask()

        # if _index == self.index:
        #     return
        # else:
        self.index = _index
        self.ui.file_list_widget.setCurrentRow(_index)

        self.pixmap_img = QPixmap(f'{self.image_dir}/{self.image_list[_index]}')
        img = self.pixmap_img.scaled(
            self.ui.viewport.width(),
            self.ui.viewport.height(),
            QtCore.Qt.KeepAspectRatio
        )

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(img)
        else:
            self.display_img.setPixmap(img)

        blank = np.zeros([self.pixmap_img.height(), self.pixmap_img.width(), 4], dtype=np.uint8)
        blank[:, :] = [253, 39, 249, 128]
        h, w, c = blank.shape
        self.pixmap_mask = QPixmap(QImage(blank, w, h, w * c, QImage.Format_ARGB32))

        self.mask = QBitmap(f'{self.image_dir}/{self.mask_list[_index]}')
        self.pixmap_mask.setMask(self.mask)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, img.width(), img.height()))
        self.img_scale = img.width() / self.pixmap_img.width()
        self.renew_buffer()
        self.update_mask()
        self.ui.prev_btn.setDisabled(False)
        self.ui.next_btn.setDisabled(False)

    # 更新 Buffer
    def update_buffer(self):
        if self.buffer_idx < (len(self.pix_buffer) - 1):
            del self.pix_buffer[self.buffer_idx + 1:]
            # print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')
        self.pix_buffer.append(self.pixmap_mask.copy())
        if len(self.pix_buffer) > self.buffer_size:
            self.pix_buffer.pop(0)
        else:
            self.buffer_idx += 1
        # print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 清空 Buffer
    def renew_buffer(self):
        self.pix_buffer.clear()
        self.buffer_idx = 0
        self.pix_buffer.append(self.pixmap_mask.copy())
        # print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 復原動作
    def undo_changes(self):
        self.buffer_idx = max(self.buffer_idx - 1, 0)
        self.ui.statusbar.showMessage(f'Undo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 重做動作
    def redo_changes(self):
        self.buffer_idx = min(self.buffer_idx + 1, len(self.pix_buffer) - 1)
        self.ui.statusbar.showMessage(f'Redo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 改變筆刷大小
    def change_brush_size(self, updateFromSpinbox: bool):
        value = self.ui.brush_size_dsb.value()
        if updateFromSpinbox:
            self.ui.brush_size_slide.setSliderPosition((value * 10) - 1)
        self.brush_size = int(value * 100)
        self.gen_brush()

    # 更新顯示遮罩
    def update_mask(self):

        if self.display_mask is None:
            mask = self.pixmap_mask.scaled(
                self.ui.viewport.width(),
                self.ui.viewport.height(),
                QtCore.Qt.KeepAspectRatio
            )
            self.display_mask = self.scene.addPixmap(mask)
        else:
            mask = self.display_img.pixmap()
            h, w = mask.height(), mask.width()
            mask = self.pixmap_mask.scaled(w, h, QtCore.Qt.KeepAspectRatio)
            self.display_mask.setPixmap(mask)

    # 產生筆刷
    def gen_brush(self):
        if self.brush_cursor is not None:
            self.scene.removeItem(self.brush_cursor)
        pen = QPen(QtCore.Qt.yellow)
        self.brush_cursor = self.scene.addEllipse(
            QtCore.QRectF(0, 0, self.brush_size, self.brush_size),
            pen,
            QBrush(QColor(255, 255, 0, 128))
        )
        self.brush_cursor.setScale(self.img_scale)

    # 擦去模式開關
    def erase_mode_flipflop(self):
        self.erase_mode = not self.erase_mode
        msg = "Switch to 'Erase' Mode" if self.erase_mode else "Switch to 'Paint' Mode"
        self.ui.statusbar.showMessage(msg)

    # 選擇圖檔資料夾
    def getfile(self):
        self.image_dir = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        print(self.image_dir)

    # 離開程式
    def on_exit(self, e):
        self.config["GeneralSettings"] = {'imagedir': self.image_dir,  # 圖片資料夾
                                          }
        self.config["WorkingState"] = {'workingimg': str(self.index),
                                       'brushsize': str(self.brush_size),
                                       'erasemode': str(int(self.erase_mode))
                                       }
        with open('settings.ini', 'w') as file:
            self.config.write(file)

    def save_mask(self):
        path = f'{self.image_dir}/{self.mask_list[self.index]}'
        # mask = self.pixmap_mask.toImage()
        # self.pixmap_mask.save(path)
        bit = self.pixmap_mask.createMaskFromColor(self.colors.BLANK)
        bit.save(path)
        self.ui.statusbar.showMessage(f'Mask image saved ({path})')

    def delete_mask(self):
        sig = []
        delete_dialog = QDialog()
        dui = Ui_DeleteDialog(sig)
        dui.setupUi(delete_dialog)
        dui.labelFilename.setText(self.mask_list[self.index])
        delete_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        delete_dialog.exec()
        if sig[0] == 1:
            idx = self.index
            moveto = (idx + 1) if idx < (len(self.image_list) - 1) else (idx - 1)
            self.ui.file_list_widget.setCurrentRow(moveto)
            path = f'{self.image_dir}/{self.mask_list[idx]}'
            os.remove(path)
            self.ui.file_list_widget.takeItem(idx)
            self.image_list.pop(idx)
            self.mask_list.pop(idx)
            self.index = moveto if idx > moveto else idx
            self.ui.statusbar.showMessage(f'File "{path}" has been deleted')



