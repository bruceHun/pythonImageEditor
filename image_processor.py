import os
from dataclasses import dataclass
import configparser
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget, QStatusBar, QListWidget, \
    QSlider, QFileDialog, QDialog, QPushButton, QSpinBox
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QBrush, QImage, QPen, QKeySequence, QMouseEvent, QKeyEvent
from PyQt5 import QtCore
from savedialog import Ui_SaveDialog
from deletedialog import Ui_DeleteDialog


@dataclass
class Colors:
    BLANK = QColor(0, 0, 0, 0)
    RED = QColor(255, 0, 0, 255)
    GREEN = QColor(0, 255, 0, 255)
    BLUE = QColor(0, 0, 255, 255)
    PINK = QColor(249, 39, 253, 255)
    YELLOW = QColor(255, 255, 0, 255)
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
    zoom_scale = 0.06
    zoom_max = 2
    zoom_min = 0.1
    # 檔案相關
    image_list = []
    mask_list = []
    image_dir = './'
    index = -1
    # 繪圖相關
    brush_size = 300
    MAX_BRUSH_SIZE = 500
    brush_cursor: QGraphicsPixmapItem = None
    painter: QPainter = None
    painting: bool = False
    erase_mode: bool = True
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
            self.config.optionxform = str
            self.config.read("settings.ini")
        except FileNotFoundError:
            self.getfile()
            self.config = configparser.ConfigParser()
            self.config.optionxform = str

            self.config["GeneralSettings"] = {'ImageDir': self.image_dir,  # 圖片資料夾
                                              'ZoomScale': '0.06',
                                              'ZoomMaxScale': '2',
                                              'ZoomMinScale': '0.1'}
            self.config["WorkingState"] = {'WorkingImg': '0',
                                           'BrushSize': '300',
                                           'Erasemode': '1'
                                           }
            with open('settings.ini', 'w') as file:
                self.config.write(file)

        self.image_dir = self.config.get('GeneralSettings', 'ImageDir')
        self.zoom_scale = min(max(float(self.config.get('GeneralSettings', 'ZoomScale')), 0), 5)
        self.zoom_max = min(max(float(self.config.get('GeneralSettings', 'ZoomMaxScale')), 1), 10)
        self.zoom_min = min(max(float(self.config.get('GeneralSettings', 'ZoomMinScale')), 0.01), 1)
        self.index = int(self.config.get('WorkingState', 'WorkingImg'))
        self.brush_size = int(self.config.get('WorkingState', 'BrushSize'))
        self.erase_mode = bool(self.config.get('WorkingState', 'Erasemode'))
        self.label_color = self.colors.PINK

        # 列出圖片檔名
        for file in os.listdir(self.image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(file[: len(file) - 9] + '.JPG')
                self.mask_list.append(file)

    def key_event(self, e: QKeyEvent):
        key = e.key()
        if key == QtCore.Qt.Key_Plus or key == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)
        if key == QtCore.Qt.Key_Minus or key == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)
        if key == QtCore.Qt.Key_Space:
            self.scale_to_fit(e)
        if key == QtCore.Qt.Key_L:
            self.save_lable_image()

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
        modifiers = int(e.modifiers())

        if modifiers and modifiers & MOD_MASK == modifiers:
            keyname = QKeySequence(modifiers).toString()

            if keyname == "Ctrl+":
                self.scale_display(delta.y() * 0.01)
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
        # Update cursor position
        t = self.ui.viewport.viewportTransform()
        r = int(self.brush_size / 2)
        curr_x = int((e.x() - t.m31()) / t.m11()) - r
        curr_y = int((e.y() - t.m32()) / t.m11()) - r
        self.brush_cursor.setPos(QtCore.QPoint(curr_x, curr_y))

    # 開始繪圖
    def start_paint(self, e: QMouseEvent):
        self.painting = True
        self.painter = QPainter(self.pixmap_mask)
        self.painter.setCompositionMode(QPainter.CompositionMode_Plus)
        p = self.painter.pen()
        p.setColor(self.label_color)
        self.painter.setPen(p)
        self.painter.setBrush(QBrush(self.label_color))
        t = self.ui.viewport.viewportTransform()
        r = int(self.brush_size / 2)
        curr_x = int((e.x() - t.m31()) / t.m11()) - r
        curr_y = int((e.y() - t.m32()) / t.m11()) - r
        self.painter.setCompositionMode(
            QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
        )
        self.painter.drawEllipse(curr_x, curr_y, self.brush_size, self.brush_size)
        self.ui.root.update()
        self.update_mask()

    # 結束繪圖
    def end_paint(self, e):
        self.painting = False
        self.unsaved_actions += 1
        self.painter.end()
        self.update_buffer()

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e: QMouseEvent):
        t = self.ui.viewport.viewportTransform()
        r = int(self.brush_size / 2)
        curr_x = int((e.x() - t.m31())/t.m11()) - r
        curr_y = int((e.y() - t.m32()) / t.m11()) - r
        if self.painting:
            self.painter.setCompositionMode(
                QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
            )
            self.painter.drawEllipse(curr_x, curr_y, self.brush_size, self.brush_size)
            self.ui.root.update()
            self.update_mask()

        self.brush_cursor.setPos(QtCore.QPoint(curr_x, curr_y))

    # 調整顯示大小
    def scale_display(self, value: float):
        # Noise removal
        if abs(value) < 0.01:
            return

        # self.ui.viewport.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        new_scale = 1 + max(min(value, self.zoom_scale), -self.zoom_scale)
        tgt_scale = self.ui.viewport.viewportTransform().m11() * new_scale
        if tgt_scale > self.zoom_max or tgt_scale < self.zoom_min:
            new_scale = 1
        self.ui.viewport.scale(new_scale, new_scale)

    # 調整 viewport 符合圖片大小
    def scale_to_fit(self, e):
        if self.display_img is not None:
            self.ui.viewport.fitInView(self.display_img, QtCore.Qt.KeepAspectRatio)

    # 切換圖片
    def change_image(self, _index: int):
        if self.save_mask() == 3:
            return

        self.ui.prev_btn.setDisabled(True)
        self.ui.next_btn.setDisabled(True)
        self.index = _index
        self.ui.file_list_widget.setCurrentRow(_index)

        self.pixmap_img = QPixmap(f'{self.image_dir}/{self.image_list[_index]}')

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(self.pixmap_img)
        else:
            self.display_img.setPixmap(self.pixmap_img)

        blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
        blank.fill(self.colors.PINK)
        self.pixmap_mask = QPixmap(blank)

        self.mask = QBitmap(f'{self.image_dir}/{self.mask_list[_index]}')
        self.pixmap_mask.setMask(self.mask)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, self.pixmap_img.width(), self.pixmap_img.height()))
        self.renew_buffer()
        self.update_mask()
        self.ui.viewport.fitInView(self.display_img, QtCore.Qt.KeepAspectRatio)
        self.ui.prev_btn.setDisabled(False)
        self.ui.next_btn.setDisabled(False)

    # 更新 Buffer
    def update_buffer(self):
        # Not at the last element of the buffer
        if self.buffer_idx < (len(self.pix_buffer) - 1):
            del self.pix_buffer[self.buffer_idx + 1:]
            print(f'After clean Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')
        self.pix_buffer.append(self.pixmap_mask.copy())
        if len(self.pix_buffer) > self.buffer_size:
            self.pix_buffer.pop(0)
        else:
            self.buffer_idx += 1
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 清空 Buffer
    def renew_buffer(self):
        self.pix_buffer.clear()
        self.buffer_idx = 0
        self.pix_buffer.append(self.pixmap_mask.copy())
        self.unsaved_actions = 0
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 復原動作
    def undo_changes(self):
        new_idx = max(self.buffer_idx - 1, 0)
        if self.buffer_idx == new_idx:
            return
        else:
            self.buffer_idx = new_idx
        self.unsaved_actions -= 1
        print(f'Undo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 重做動作
    def redo_changes(self):
        new_idx = min(self.buffer_idx + 1, len(self.pix_buffer) - 1)
        if self.buffer_idx == new_idx:
            return
        else:
            self.buffer_idx = new_idx
        self.unsaved_actions += 1
        print(f'Redo to Buffer Index: {self.buffer_idx}')
        self.pixmap_mask = self.pix_buffer[self.buffer_idx]
        self.update_mask()

    # 改變筆刷大小
    def change_brush_size(self, updateFromSpinbox: bool):
        value = self.ui.brush_size_sb.value()
        if updateFromSpinbox:
            self.ui.brush_size_slide.setSliderPosition((value / self.MAX_BRUSH_SIZE)*100 - 1)
        self.brush_size = value
        self.gen_brush()

    # 改變筆刷顏色
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
            self.display_mask = self.scene.addPixmap(self.pixmap_mask)
            self.display_mask.setOpacity(0.5)
        else:
            self.display_mask.setPixmap(self.pixmap_mask)

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
        self.brush_cursor.setOpacity(0.5)

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

        self.config["GeneralSettings"] = {'ImageDir': self.image_dir,  # 圖片資料夾
                                          'ZoomScale': str(self.zoom_scale),
                                          'ZoomMaxScale': str(self.zoom_max),
                                          'ZoomMinScale': str(self.zoom_min)}
        self.config["WorkingState"] = {'WorkingImg': str(self.index),
                                       'BrushSize': str(self.brush_size),
                                       'Erasemode': str(int(self.erase_mode))
                                       }
        with open('settings.ini', 'w') as file:
            self.config.write(file)

    # 儲存 label 圖片
    def save_lable_image(self):
        sig = []
        save_dialog = QDialog()
        dui = Ui_SaveDialog(sig)
        dui.setupUi(save_dialog)
        save_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        save_dialog.exec()
        if sig[0] == 3:
            return 3
        if sig[0] == 1:
            path = f'{self.image_dir}/{self.image_list[self.index]}'
            path = path[: len(path) - 4] + '.png'
            image = self.pixmap_mask.toImage().convertToFormat(QImage.Format_RGB32)
            image.save(path)
            self.ui.statusbar.showMessage(f'lLabel image saved ({path})')
            return 1
        if sig[0] == 2:
            return 2

    # 儲存遮罩圖片
    def save_mask(self):
        if self.unsaved_actions == 0:
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

    # 刪除遮罩圖片
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



