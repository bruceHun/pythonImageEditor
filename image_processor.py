import os
from dataclasses import dataclass
import configparser
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget, QStatusBar, QListWidget, \
    QSlider, QFileDialog, QDialog, QPushButton, QDoubleSpinBox, QSpinBox
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QBrush, QImage, QPen, QKeySequence
from PyQt5 import QtCore
from savedialog import Ui_SaveDialog
from deletedialog import Ui_DeleteDialog


@dataclass
class Colors:
    BLANK = QColor(0, 0, 0, 0)
    RED = QColor(255, 0, 0, 128)
    GREEN = QColor(0, 255, 0, 128)
    BLUE = QColor(0, 0, 255, 128)
    PINK = QColor(249, 39, 253, 128)
    YELLOW = QColor(255, 255, 0, 128)
    WHITE = QColor(255, 255, 255, 255)


class UIReferences:
    root: QWidget = None
    viewport: QGraphicsView = None
    statusbar: QStatusBar = None
    file_list_widget: QListWidget = None
    brush_size_slide: QSlider = None
    brush_size_sb: QSpinBox = None
    prev_btn: QPushButton = None
    next_btn: QPushButton = None

    def __init__(self,
                 _root: QWidget,
                 _viewport: QGraphicsView,
                 _statusbar: QStatusBar,
                 _file_list_widget: QListWidget,
                 _brush_size_slide: QSlider,
                 _brush_size_sb: QSpinBox,
                 _prev_btn: QPushButton,
                 _next_btn: QPushButton
                 ):
        self.root = _root
        self.viewport = _viewport
        self.statusbar = _statusbar
        self.file_list_widget = _file_list_widget
        self.brush_size_slide = _brush_size_slide
        self.brush_size_sb = _brush_size_sb
        self.prev_btn = _prev_btn
        self.next_btn = _next_btn


MOD_MASK = (QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.SHIFT | QtCore.Qt.META)


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
    viewport_scale = 1.0
    brush_size = 300
    brush_pos: QtCore.QPoint = QtCore.QPoint(0, 0)
    MAX_BRUSH_SIZE = 500
    MAX_WIDTH = 2160
    MIN_WIDTH = 340
    brush_cursor: QGraphicsPixmapItem = None
    painter: QPainter = None
    painting: bool = False
    erase_mode: bool = True
    label_mode: bool = False
    label_color: QColor = False
    mask: QBitmap = None
    colors = Colors()
    unsaved_actions: int = 0
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
        self.label_color = self.colors.PINK

        # 列出圖片檔名
        for file in os.listdir(self.image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(file[: len(file) - 9] + '.JPG')
                self.mask_list.append(file)

    def key_event(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Plus or key == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)
        if key == QtCore.Qt.Key_Minus or key == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)
        # if key == QtCore.Qt.Key_Left:
        #     self.change_image(max(self.index - 1, 0))
        # if key == QtCore.Qt.Key_Right:
        #     self.change_image(min(self.index + 1, len(self.image_list) - 1))

        modifiers = int(e.modifiers())
        if (modifiers and modifiers & MOD_MASK == modifiers and
                key > 0 and key != QtCore.Qt.Key_Shift and key != QtCore.Qt.Key_Alt and
                key != QtCore.Qt.Key_Control and key != QtCore.Qt.Key_Meta):
            keyname = QKeySequence(modifiers + key).toString()
            # self.ui.statusbar.showMessage(keyname)
            if keyname == "Ctrl+Z":
                self.undo_changes()
            if keyname == "Ctrl+Shift+Z":
                self.redo_changes()
            if keyname == "Ctrl+S":
                self.save_mask()

    def mouse_wheel_event(self, e):
        delta: QtCore.QPoint = e.pixelDelta()
        if delta is None:
            delta = e.angleDelta()
        self.ui.statusbar.showMessage(f'delta: ({delta.x()},{delta.y()})')
        modifiers = int(e.modifiers())

        if modifiers and modifiers & MOD_MASK == modifiers:
            keyname = QKeySequence(modifiers).toString()

            if keyname == "Ctrl+":
                self.scale_display(delta.y())
            if keyname == "Alt+":
                value = self.ui.brush_size_slide.value() + delta.y()
                self.ui.brush_size_slide.setValue(value)
                self.change_brush_size(value)
            if keyname == "Shift+":
                value = self.ui.viewport.horizontalScrollBar().value() + delta.y()
                self.ui.viewport.horizontalScrollBar().setValue(value)
        else:
            value = self.ui.viewport.verticalScrollBar().value() + delta.y()
            self.ui.viewport.verticalScrollBar().setValue(value)

    # 開始繪圖
    def start_paint(self, e):
        self.painting = True
        self.painter = QPainter(self.pixmap_mask)
        self.painter.setCompositionMode(QPainter.CompositionMode_Plus)
        p = self.painter.pen()
        p.setColor(self.label_color)
        self.painter.setPen(p)
        self.painter.setBrush(QBrush(self.label_color))
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
        self.unsaved_actions += 1
        self.painter.end()
        self.update_buffer()

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e):
        self.brush_pos = QtCore.QPoint(e.x(), e.y())
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
        if (w + value) > self.MAX_WIDTH or (w + value) < self.MIN_WIDTH:
            return
        image = self.pixmap_img.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.display_img.setPixmap(image)
        image = self.pixmap_mask.scaled(w + value, h + value, QtCore.Qt.KeepAspectRatio)
        self.display_mask.setPixmap(image)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, image.width(), image.height()))
        self.img_scale = image.width() / self.pixmap_img.width()
        self.brush_cursor.setScale(self.img_scale)

    def scale_to_fit(self, e):
        if self.pixmap_img is None or self.display_img is None:
            return
        img = self.pixmap_img.scaled(
            self.ui.viewport.width(),
            self.ui.viewport.height(),
            QtCore.Qt.KeepAspectRatio
        )
        self.display_img.setPixmap(img)
        mask = self.pixmap_mask.scaled(
            self.ui.viewport.width(),
            self.ui.viewport.height(),
            QtCore.Qt.KeepAspectRatio
        )
        self.display_mask.setPixmap(mask)
        self.img_scale = img.width() / self.pixmap_img.width()
        self.brush_cursor.setScale(self.img_scale)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, img.width(), img.height()))

    # 切換圖片
    def change_image(self, _index: int):
        if self.save_mask() == 3:
            return

        self.ui.prev_btn.setDisabled(True)
        self.ui.next_btn.setDisabled(True)
        self.index = _index
        self.ui.file_list_widget.setCurrentRow(_index)

        self.pixmap_img = QPixmap(f'{self.image_dir}/{self.image_list[_index]}')
        img = self.pixmap_img.scaled(
            self.ui.viewport.width(),
            self.ui.viewport.height(),
            QtCore.Qt.KeepAspectRatio
        )
        self.img_scale = img.width() / self.pixmap_img.width()

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(img)
        else:
            self.display_img.setPixmap(img)

        if self.brush_cursor is not None:
            self.brush_cursor.setScale(self.img_scale)

        blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
        blank.fill(self.colors.PINK)
        self.pixmap_mask = QPixmap(blank)

        self.mask = QBitmap(f'{self.image_dir}/{self.mask_list[_index]}')
        self.pixmap_mask.setMask(self.mask)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, img.width(), img.height()))
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
        self.unsaved_actions = 0
        # print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 復原動作
    def undo_changes(self):
        self.unsaved_actions -= 1
        self.buffer_idx = max(self.buffer_idx - 1, 0)
        self.ui.statusbar.showMessage(f'Undo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 重做動作
    def redo_changes(self):
        self.unsaved_actions += 1
        self.buffer_idx = min(self.buffer_idx + 1, len(self.pix_buffer) - 1)
        self.ui.statusbar.showMessage(f'Redo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 改變筆刷大小
    def change_brush_size(self, updateFromSpinbox: bool):
        value = self.ui.brush_size_sb.value()
        if updateFromSpinbox:
            self.ui.brush_size_slide.setSliderPosition((value / self.MAX_BRUSH_SIZE)*100 - 1)
        self.brush_size = value
        self.gen_brush()

    def change_brush_color(self, index: int):
        if index == 0:
            self.label_color = self.colors.RED
        if index == 1:
            self.label_color = self.colors.GREEN
        if index == 2:
            self.label_color = self.colors.BLUE
        if index == 3:
            self.label_color = self.colors.PINK

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
            QBrush(self.colors.YELLOW)
        )
        self.brush_cursor.setScale(self.img_scale)
        t = self.ui.viewport.transform()
        offset = int((self.brush_size * self.img_scale) / 2)
        self.brush_cursor.setPos(QtCore.QPoint(int(self.brush_pos.x() - offset - t.m31()), int(self.brush_pos.y() - offset - t.m32())))

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
        if len(self.pix_buffer) > 1:
            self.save_mask()

        self.config["GeneralSettings"] = {'imagedir': self.image_dir,  # 圖片資料夾
                                          }
        self.config["WorkingState"] = {'workingimg': str(self.index),
                                       'brushsize': str(self.brush_size),
                                       'erasemode': str(int(self.erase_mode))
                                       }
        with open('settings.ini', 'w') as file:
            self.config.write(file)

    def save_mask(self):
        if self.unsaved_actions <= 0:
            return 0
        sig = []
        save_dialog = QDialog()
        dui = Ui_SaveDialog(sig)
        dui.setupUi(save_dialog)
        save_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        save_dialog.exec()
        if sig[0] == 3:
            return 3
        if sig[0] == 1:
            path = f'{self.image_dir}/{self.mask_list[self.index]}'
            bit = self.pixmap_mask.createMaskFromColor(self.colors.BLANK)
            bit.save(path)
            self.ui.statusbar.showMessage(f'Mask image saved ({path})')
            return 1
        if sig[0] == 2:
            return 2

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



