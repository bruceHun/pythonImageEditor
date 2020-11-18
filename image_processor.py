from dataclasses import dataclass
import configparser

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QFileDialog, QMainWindow, QGraphicsView, QDialog
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QBrush, QImage, QPen, QKeySequence, QMouseEvent, QKeyEvent, \
    QWheelEvent, QPolygon, QTransform
from PyQt5 import QtCore
from mainwindow import Ui_MainWindow
from image_buffer_module import ImageBufferModule
from file_manager import FileManager
from settingsdialog import Ui_DialogSettings
from lineeditdialog import Ui_DialogLineEdit


@dataclass
class Colors:
    BLANK = QColor(0, 0, 0, 0)
    RED = QColor(255, 0, 0, 255)
    GREEN = QColor(0, 255, 0, 255)
    BLUE = QColor(0, 0, 255, 255)
    YELLOW = QColor(255, 255, 0, 255)
    FUCHSIA = QColor(255, 0, 255, 255)
    AQUA = QColor(0, 255, 255, 255)
    DRED = QColor(128, 0, 0, 255)
    DGREEN = QColor(0, 128, 0, 255)
    DBLUE = QColor(0, 0, 128, 255)
    DYELLOW = QColor(128, 128, 0, 255)
    DFUCHSIA = QColor(128, 0, 128, 255)
    DAQUA = QColor(0, 128, 128, 255)
    WHITE = QColor(255, 255, 255, 255)


MOD_MASK = (QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.SHIFT | QtCore.Qt.META)


def get_directory():
    filedir = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
    print(f'image dir : "{filedir}"')
    return filedir


class ImageProcessor:
    #
    labeling_mode: bool = True
    pixmap_img: QPixmap = None
    pixmap_mask = {}
    default_class = 'vechicle'
    pixmap_brush: QPixmap = None
    display_img: QGraphicsPixmapItem = None
    display_mask = {}
    scene: QGraphicsScene = None
    zoom_scale = 0.1
    zoom_max = 2
    # 檔案相關
    FM: FileManager = FileManager()
    # 繪圖相關
    brush_size = 300
    brush_cursor: QGraphicsPixmapItem = None
    painter: QPainter = None
    painting: bool = False
    erase_mode: bool = True
    label_color: QColor = False
    mask: QBitmap = None
    colors = Colors()
    # 操作設定相關
    scroll_speed = -5
    # 繪圖緩衝區模組
    ab: ImageBufferModule = ImageBufferModule()
    # 上層顯示物件
    ui: Ui_MainWindow = None
    main_window: QMainWindow = None
    # 設定檔解析器
    config: configparser = None

    def init(self, is_running: bool = False):
        if is_running:
            directory = get_directory()
            if directory == "":
                return
            else:
                self.FM.image_dir = directory
                self.FM.image_list.clear()
                self.ui.listWidget.clear()

        # 開啟設定檔
        try:
            settings = open("settings.ini", "r")
            settings.close()
            self.config = configparser.ConfigParser()
            self.config.optionxform = str
            self.config.read("settings.ini")
        except FileNotFoundError:
            if not is_running:
                self.FM.image_dir = get_directory()
            if self.FM.image_dir == "":
                self.FM.image_dir = "./"
            self.config = configparser.ConfigParser()
            self.config.optionxform = str

            self.config["GeneralSettings"] = {'ImageDir': self.FM.image_dir,  # 圖片資料夾
                                              'DefaultClass': 'object',
                                              'ZoomScale': '0.1',
                                              'ZoomMaxScale': '5',
                                              'InvertScroll': 'False'}
            self.config["WorkingState"] = {'WorkingImg': '0',
                                           'BrushSize': '300',
                                           'Erasemode': '1'
                                           }
            with open('settings.ini', 'w') as file:
                self.config.write(file)

        # 載入新目錄時套用預設工作階段設定
        if is_running:
            self.zoom_scale = 0.1
            self.zoom_max = 5
            self.FM.index = 0
            self.brush_size = 300
            self.erase_mode = True
            self.scroll_speed = -5
        else:
            self.FM.image_dir = self.config.get('GeneralSettings', 'ImageDir')
            self.default_class = self.config.get('GeneralSettings', 'DefaultClass')
            self.zoom_scale = min(max(float(self.config.get('GeneralSettings', 'ZoomScale')), 0), 5)
            self.zoom_max = min(max(float(self.config.get('GeneralSettings', 'ZoomMaxScale')), 1), 10)
            self.scroll_speed = 5 if self.config.get('GeneralSettings', 'InvertScroll') == 'True' else -5
            self.FM.index = int(self.config.get('WorkingState', 'WorkingImg'))
            self.brush_size = int(self.config.get('WorkingState', 'BrushSize'))
            self.erase_mode = bool(self.config.get('WorkingState', 'Erasemode'))
        self.label_color = self.colors.FUCHSIA

        # 列出圖片檔名
        self.FM.get_file_lists(self.labeling_mode)
        if is_running:
            self.ui.listWidget.addItems(self.FM.image_list)
            self.change_image(0)

    def key_event(self, e: QKeyEvent):
        key = e.key()
        if key == QtCore.Qt.Key_Plus or key == QtCore.Qt.Key_BracketRight:
            self.scale_display(self.zoom_scale)
        if key == QtCore.Qt.Key_Minus or key == QtCore.Qt.Key_BracketLeft:
            self.scale_display(-self.zoom_scale)
        if key == QtCore.Qt.Key_Space:
            self.scale_to_fit(e)

    def mouse_wheel_event(self, e: QWheelEvent):
        delta: QtCore.QPoint = e.pixelDelta()
        if delta is None or delta.y() == 0:
            delta = e.angleDelta() / 10
        modifiers = int(e.modifiers())

        if modifiers and modifiers & MOD_MASK == modifiers:
            keyname = QKeySequence(modifiers).toString()
            if keyname == "Ctrl+":
                oldpos = self.ui.graphicsView.mapToScene(e.pos())
                self.scale_display(delta.y() * 0.01)
                newpos = self.ui.graphicsView.mapToScene(e.pos())
                deltapos = newpos - oldpos
                self.ui.graphicsView.translate(deltapos.x(), deltapos.y())
            if keyname == "Ctrl+Shift+":
                value = self.ui.BrushSizeSlider.value() + delta.y()
                self.ui.BrushSizeSlider.setValue(value)
            if keyname == "Shift+":
                delta *= self.scroll_speed
                value = self.ui.graphicsView.horizontalScrollBar().value() + delta.y()
                self.ui.graphicsView.horizontalScrollBar().setValue(value)
        else:
            delta *= self.scroll_speed
            value = self.ui.graphicsView.verticalScrollBar().value() + delta.y()
            self.ui.graphicsView.verticalScrollBar().setValue(value)
        # Update cursor position
        t = self.ui.graphicsView.viewportTransform()
        r = int(self.brush_size / 2)
        curr_x = int((e.x() - t.m31()) / t.m11()) - r
        curr_y = int((e.y() - t.m32()) / t.m11()) - r
        self.brush_cursor.setPos(QtCore.QPoint(curr_x, curr_y))

    # 開始繪圖
    def start_paint(self, e: QMouseEvent):
        self.painting = True
        self.painter = QPainter(self.pixmap_mask[self.ui.comboBox.currentText()])
        p = self.painter.pen()
        p.setColor(self.label_color)
        self.painter.setPen(p)
        self.painter.setBrush(QBrush(self.label_color))
        t = self.ui.graphicsView.viewportTransform()
        r = int(self.brush_size / 2)
        curr_x = int((e.x() - t.m31()) / t.m11()) - r
        curr_y = int((e.y() - t.m32()) / t.m11()) - r
        self.painter.setCompositionMode(
            QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
        )
        self.painter.drawEllipse(curr_x, curr_y, self.brush_size, self.brush_size)
        self.ui.centralwidget.update()
        self.update_mask()

    # 結束繪圖
    def end_paint(self, e):
        self.painting = False
        self.ab.unsaved_actions += 1
        self.painter.end()
        self.ab.push(self.ui.comboBox.currentText(), self.pixmap_mask[self.ui.comboBox.currentText()])

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e: QMouseEvent):
        # t = self.ui.graphicsView.viewportTransform()
        r = int(self.brush_size / 2)
        # curr_x = int((e.x() - t.m31()) / t.m11()) - r
        # curr_y = int((e.y() - t.m32()) / t.m11()) - r
        mappos = self.ui.graphicsView.mapToScene(e.pos())
        curr_x, curr_y = mappos.x() - r, mappos.y() - r
        if self.painting:
            self.painter.setCompositionMode(
                QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
            )
            self.painter.drawEllipse(curr_x, curr_y, self.brush_size, self.brush_size)
            # self.ui.centralwidget.update()
            self.update_mask()

        self.brush_cursor.setPos(QtCore.QPoint(curr_x, curr_y))

    # 調整顯示大小
    def scale_display(self, value: float):
        # Noise removal
        if abs(value) < 0.01:
            return

        new_scale = 1 + max(min(value, self.zoom_scale), -self.zoom_scale)
        tgt_scale = self.ui.graphicsView.viewportTransform().m11() * new_scale
        if tgt_scale > self.zoom_max:
            new_scale = 1
        self.ui.graphicsView.scale(new_scale, new_scale)
        t = self.ui.graphicsView.viewportTransform()
        if t.m31() > 0 and t.m32() > 0:
            self.scale_to_fit()

    # 調整 viewport 符合圖片大小
    def scale_to_fit(self, e: QWheelEvent = None):
        if self.display_img is not None:
            self.ui.graphicsView.fitInView(self.display_img, QtCore.Qt.KeepAspectRatio)

    # 切換圖片
    def change_image(self, _index: int):
        if self.labeling_mode and self.save_annotation() == 3:
            return
        elif not self.labeling_mode and self.save_mask() == 3:
            return

        self.ui.FuncBtn1.setDisabled(True)
        self.ui.FuncBtn2.setDisabled(True)
        self.FM.index = _index
        self.ui.listWidget.setCurrentRow(_index)

        self.pixmap_img = QPixmap(f'{self.FM.image_dir}/{self.FM.image_list[_index]}')

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(self.pixmap_img)
        else:
            self.display_img.setPixmap(self.pixmap_img)

        blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
        self.pixmap_mask.clear()
        for key, item in self.display_mask.items():
            self.scene.removeItem(item)
        self.display_mask.clear()

        # 利用 label 檔的輪廓資訊繪製遮罩
        if self.labeling_mode:
            if len(self.FM.annotations) > 0:
                try:
                    a = self.FM.annotations[self.FM.image_list[_index]]
                    self.ui.statusbar.showMessage(f"{len(a['regions'])} annotation(s) loaded")
                    # polygons = [r['shape_attributes'] for r in a['regions']]

                    labelcolors = [
                        self.colors.RED,
                        self.colors.GREEN,
                        self.colors.BLUE,
                        self.colors.YELLOW,
                        self.colors.FUCHSIA,
                        self.colors.AQUA
                    ]
                    nameref = {'Red': 0, 'Green': 1, 'Blue': 2, 'Yellow': 3, 'Fuchsia': 4, 'Aqua': 5}
                    cidx = 0

                    for r in a['regions']:
                        area = QPolygon()
                        p = r['shape_attributes']
                        for i in range(len(p['all_points_x'])):
                            area.append(QPoint(p['all_points_x'][i], p['all_points_y'][i]))

                        try:
                            paint_color = labelcolors[nameref[r['region_attributes']['Color']]]
                        except KeyError:
                            paint_color = labelcolors[cidx]
                            cidx = (cidx + 1) % 6

                        # Painting prep
                        print('Getting class name')
                        classname = r['region_attributes']['Name']
                        print(classname)
                        try:
                            self.pixmap_mask[classname]
                        except KeyError:
                            self.pixmap_mask[classname] = QPixmap(blank)

                        self.painter = QPainter(self.pixmap_mask[classname])
                        self.painter.setCompositionMode(QPainter.CompositionMode_Source)
                        self.painter.setPen(QPen(paint_color))
                        self.painter.setBrush(QBrush(paint_color))
                        self.painter.drawPolygon(area)
                        self.painter.end()

                except KeyError:
                    self.ui.statusbar.showMessage('No annotation for this image')
        # 讀取圖檔建立遮罩圖層
        else:
            f_name = self.FM.image_list[_index]
            f_name = f_name[:len(f_name)-4]
            self.mask = QBitmap(f'{self.FM.image_dir}/{f_name}_mask.tif')
            if not self.mask.isNull():
                blank.fill(self.colors.FUCHSIA)
                self.pixmap_mask = QPixmap(blank)
                self.pixmap_mask.setMask(self.mask)
                self.ui.statusbar.showMessage('')
            else:
                self.ui.statusbar.showMessage(f'No mask file for {self.FM.image_list[_index]}')
                self.pixmap_mask = QPixmap(blank)

        # 沒有資料導入 創建預設類別圖層
        if len(self.pixmap_mask) == 0:
            self.pixmap_mask[self.default_class] = QPixmap(blank)
        self.ui.comboBox.clear()

        # populate Class 下拉式清單
        for key, val in self.pixmap_mask.items():
            self.ui.comboBox.addItem(key)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, self.pixmap_img.width(), self.pixmap_img.height()))
        self.ab.renew_buffer(self.pixmap_mask)
        self.update_mask()
        self.ui.graphicsView.fitInView(self.display_img, QtCore.Qt.KeepAspectRatio)
        self.main_window.setWindowTitle(f'Mask Editor -- {self.FM.image_list[_index]}')

        self.ui.FuncBtn1.setDisabled(False)
        self.ui.FuncBtn2.setDisabled(False)

    # 更新顯示遮罩
    def update_mask(self):
        if self.painting:
            classname = self.ui.comboBox.currentText()
            pixmap = self.pixmap_mask[classname]
            try:
                self.display_mask[classname].setPixmap(pixmap)
            except KeyError:
                self.display_mask[classname] = self.scene.addPixmap(pixmap)
                self.display_mask[classname].setOpacity(0.5)
        else:
            for classname, pixmap in self.pixmap_mask.items():
                try:
                    self.display_mask[classname].setPixmap(pixmap)
                except KeyError:
                    self.display_mask[classname] = self.scene.addPixmap(pixmap)
                    self.display_mask[classname].setOpacity(0.5)

    # 復原動作
    def undo_changes(self):
        item = self.ab.undo_changes(self.ui.comboBox.currentText())
        if item is not None:
            self.pixmap_mask[item.c_name] = item.data
            self.update_mask()
            print(f'Undo to Buffer Index: {self.ab.buffer_idx}, class: {item.c_name}')

    # 重做動作
    def redo_changes(self):
        item = self.ab.redo_changes()
        if item is not None:
            self.pixmap_mask[item.c_name] = item.data
            self.update_mask()

    # 改變筆刷大小
    def change_brush_size(self):
        value = self.ui.BrushSizeSlider.value()
        self.brush_size = value
        self.gen_brush()

    # 改變筆刷顏色
    def change_brush_color(self, index: int):
        if self.erase_mode:
            self.erase_mode = False
        if index == 0:
            self.label_color = self.colors.RED
        elif index == 1:
            self.label_color = self.colors.GREEN
        elif index == 2:
            self.label_color = self.colors.BLUE
        elif index == 3:
            self.label_color = self.colors.YELLOW
        elif index == 4:
            self.label_color = self.colors.FUCHSIA
        elif index == 5:
            self.label_color = self.colors.AQUA
        self.gen_brush()

    # 改變底圖亮度
    def change_photo_brightness(self):
        value = self.ui.brightnessSlider.value() / 100
        self.display_img.setOpacity(value)
        if value < 0.5:
            self.display_mask[self.ui.comboBox.currentText()].setOpacity(1 - value)

    # 產生筆刷
    def gen_brush(self):
        if self.brush_cursor is not None:
            self.scene.removeItem(self.brush_cursor)
        brush_color = None
        if self.erase_mode:
            brush_color = self.colors.WHITE
        elif self.label_color == self.colors.RED:
            brush_color = self.colors.DRED
        elif self.label_color == self.colors.GREEN:
            brush_color = self.colors.DGREEN
        elif self.label_color == self.colors.BLUE:
            brush_color = self.colors.DBLUE
        elif self.label_color == self.colors.YELLOW:
            brush_color = self.colors.DYELLOW
        elif self.label_color == self.colors.FUCHSIA:
            brush_color = self.colors.DFUCHSIA
        elif self.label_color == self.colors.AQUA:
            brush_color = self.colors.DAQUA
        pen = QPen(brush_color)
        self.brush_cursor = self.scene.addEllipse(
            QtCore.QRectF(0, 0, self.brush_size, self.brush_size),
            pen,
            QBrush(brush_color)
        )
        self.brush_cursor.setOpacity(0.5)

    # 擦去模式開關
    def erase_mode_on(self):
        self.erase_mode = True
        self.gen_brush()

    # 離開程式
    def on_exit(self, e):
        if len(self.ab.pix_buffer) > 1:
            self.save_mask()

        self.config["GeneralSettings"] = {'ImageDir': self.FM.image_dir,  # 圖片資料夾
                                          'DefaultClass': self.default_class,
                                          'ZoomScale': str(self.zoom_scale),
                                          'ZoomMaxScale': str(self.zoom_max),
                                          'InvertScroll': 'False' if self.scroll_speed < 0 else 'True'}
        self.config["WorkingState"] = {'WorkingImg': str(self.FM.index),
                                       'BrushSize': str(self.brush_size),
                                       'Erasemode': str(int(self.erase_mode))
                                       }
        with open('settings.ini', 'w') as file:
            self.config.write(file)

    def save_mask(self):
        if self.ab.unsaved_actions != 0:
            self.FM.save_mask(self.pixmap_mask)

    def save_annotation(self):
        if self.ab.unsaved_actions != 0:
            self.FM.save_annotation(self.pixmap_mask)

    def save_label_image(self):
        self.FM.save_label_image(self.pixmap_mask)

    def delete_mask(self):
        self.FM.delete_mask()

    def change_settings(self):
        dialog_settings = QDialog()
        ui = Ui_DialogSettings()
        ui.setupUi(dialog_settings)

        ui.lineEdit.setText(self.FM.image_dir)
        ui.lineEdit_2.setText(self.default_class)
        ui.lineEdit_3.setText(str(self.zoom_scale))
        ui.lineEdit_4.setText(str(self.zoom_max))

        res = dialog_settings.exec()
        if res == QDialog.Accepted:
            if ui.lineEdit_2.text() != "":
                self.default_class = ui.lineEdit_2.text()
            if ui.lineEdit_3.text() != "":
                self.zoom_scale = max(min(float(ui.lineEdit_3.text()), 2), 0.01)
            if ui.lineEdit_4.text() != "":
                self.zoom_max = max(min(float(ui.lineEdit_4.text()), 10), 2)
            # update changes
            self.change_image(self.FM.index)

    def add_class(self):
        dialog_line_edit = QDialog()
        ui = Ui_DialogLineEdit()
        ui.setupUi(dialog_line_edit)
        dialog_line_edit.setWindowTitle('Add Class')
        ui.label.setText('Please enter the name of the new class')
        res = dialog_line_edit.exec()

        if res == QDialog.Accepted and ui.lineEdit.text() != "":
            blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
            newclass = ui.lineEdit.text().replace(" ", "")
            self.pixmap_mask[newclass] = QPixmap(blank)
            self.ui.comboBox.addItem(newclass)



