from dataclasses import dataclass
from configparser import ConfigParser, NoOptionError
from os import path as os_path
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QFileDialog, QMainWindow, QDialog, QGraphicsLineItem, \
    QMessageBox, QGraphicsPathItem, QGraphicsSimpleTextItem
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QBrush, QImage, QPen, QKeySequence, QMouseEvent, \
    QKeyEvent, QWheelEvent, QPolygon, QPolygonF, QPainterPath, QCursor, QFont
from PyQt5 import QtCore
from mainwindow import Ui_MainWindow
from image_buffer_module import ImageBufferManager
from file_manager import FileManager
from dialog_settings import Ui_DialogSettings
from dialog_line_edit import Ui_DialogLineEdit
from enum import Enum
from threading import Thread, Lock
from typing import Union
import csv
import re


class PMode(Enum):
    Brush = 1
    Select = 2


class MMode(Enum):
    Neutral = 0
    Painting = 1
    Grabing = 2


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
    ORANGE = QColor(255, 165, 0, 255)
    SANDYBROWN = QColor(244, 164, 96, 255)


label_colors: list = [
                    Colors.RED,
                    Colors.GREEN,
                    Colors.BLUE,
                    Colors.YELLOW,
                    Colors.FUCHSIA,
                    Colors.AQUA
                ]
nameref = {'Red': 0, 'Green': 1, 'Blue': 2, 'Yellow': 3, 'Fuchsia': 4, 'Aqua': 5}
MOD_MASK = (QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.SHIFT | QtCore.Qt.META)


def get_directory():
    filedir = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
    print(f'image dir : "{filedir}"')
    return filedir


def paint_regions_by_class(_pixmap: QPixmap, _data: list):
    """

    :param _pixmap:
    :param _data:
    :return:
    """
    # Painting prep
    pt = QPainter(_pixmap)
    pt.setCompositionMode(QPainter.CompositionMode_Source)
    for region in _data:
        pt.setPen(QPen(region[0]))
        pt.setBrush(QBrush(region[0]))
        pt.drawPolygon(region[1])
    pt.end()


class ImageProcessor:

    is_processing: bool = False

    def __init__(self):
        self.prev_pos: QPoint = QPoint()
        self.pixmap_img: Union[QPixmap, None] = None
        self.pixmap_mask = {}
        self.default_classes = ''
        self.default_layers: list = []
        self.pixmap_brush: Union[QPixmap, None] = None
        self.display_img: Union[QGraphicsPixmapItem, None] = None
        self.display_sel: Union[QGraphicsPathItem, None] = None
        self.display_line: Union[QGraphicsLineItem, None] = None
        self.display_mask = {}
        self.layer_hidden: dict = {}
        self.layer_highlight: bool = False
        self.scene: Union[QGraphicsScene, None] = None
        self.zoom_scale = 0.1
        self.zoom_max = 2
        self.tag_size = 32
        self.show_tag: bool = True
        # 檔案相關
        self.FM: FileManager = FileManager()
        # 繪圖相關
        self.brush_size = 300
        self.brush_cursor: Union[QGraphicsPixmapItem, None] = None
        self.painter: Union[QPainter, None] = None
        self.m_mode: MMode = MMode.Neutral
        self.paint_mode: PMode = PMode.Brush
        self.selections_pnt: list = []
        self.erase_mode: bool = True
        self.label_color: int = 0
        self.mask: Union[QBitmap, None] = None
        self.prev_pos: QPoint = QPoint(0, 0)
        self.border: int = 50
        # 操作設定相關
        self.scroll_speed = 5
        # 繪圖緩衝區模組
        self.BM: ImageBufferManager = ImageBufferManager()
        # 上層顯示物件
        self.UI: Union[Ui_MainWindow, None] = None
        self.main_window: Union[QMainWindow, None] = None
        # 設定檔解析器
        self.config: Union[ConfigParser, None] = None
        # 目前指派顏色序號
        self.cidx: int = 0
        self.total_items: str = ''

    def init(self, is_running: bool = False, show_annotated_switch: bool = False):
        """

        :param is_running:
        :param show_annotated_switch:
        :return:
        """
        if is_running and not show_annotated_switch:
            directory = get_directory()
            if directory == "":
                return
            else:
                self.FM.image_dir = directory
                print(self.FM.image_dir)
                self.FM.image_list.clear()
                self.UI.listWidget.clear()
        if show_annotated_switch:
            self.FM.image_list.clear()
            self.UI.listWidget.clear()

        # 開啟設定檔
        self.config = ConfigParser()
        self.config.optionxform = str
        try:
            settings = open("settings.ini", "r")
            settings.close()
            self.config.read("settings.ini")
        except FileNotFoundError:
            if not is_running:
                self.FM.image_dir = get_directory()
            if self.FM.image_dir == "":
                self.FM.image_dir = "./"

            self.config["GeneralSettings"] = {'ImageDir': self.FM.image_dir,  # 圖片資料夾
                                              'DefaultClasses': '',
                                              'ZoomScale': 0.1,
                                              'ZoomMaxScale': 5,
                                              'InvertScroll': 'False',
                                              'BorderInPixels': 50,
                                              'ShowClassNameTag': 1,
                                              'ClassNameTagFontSize': 32
                                              }
            self.config["WorkingState"] = {'WorkingImg': '0',
                                           'BrushSize': '300',
                                           'BrushColor': 0,
                                           'Erasemode': 0,
                                           'ShowAnnotated': 0
                                           }
            with open('settings.ini', 'w') as file:
                self.config.write(file)

        success = True
        try:
            if not is_running:
                self.FM.image_dir = self.config.get('GeneralSettings', 'ImageDir')
                self.default_classes = self.config.get('GeneralSettings', 'DefaultClasses')
                self.zoom_scale = min(max(float(self.config.get('GeneralSettings', 'ZoomScale')), 0), 5)
                self.zoom_max = min(max(float(self.config.get('GeneralSettings', 'ZoomMaxScale')), 1), 10)
                self.scroll_speed *= 1 if self.config.get('GeneralSettings', 'InvertScroll') == 'True' else -1
                self.show_tag = int(self.config.get('GeneralSettings', 'ShowClassNameTag'))
                self.tag_size = int(self.config.get('GeneralSettings', 'ClassNameTagFontSize'))
                self.border = int(self.config.get('GeneralSettings', 'BorderInPixels'))
                self.FM.index = int(self.config.get('WorkingState', 'WorkingImg'))
                self.brush_size = int(self.config.get('WorkingState', 'BrushSize'))
                self.label_color = int(self.config.get('WorkingState', 'BrushColor'))
                self.erase_mode = bool(int(self.config.get('WorkingState', 'Erasemode')))
            if not show_annotated_switch:
                self.UI.action_Show_annotated.setChecked(int(self.config.get('WorkingState', 'ShowAnnotated')))
        except NoOptionError:
            success = False

        # 載入新目錄或讀取錯誤時套用預設工作階段設定
        if is_running or not success:
            self.zoom_scale = 0.1
            self.zoom_max = 5
            self.FM.index = 0
            self.brush_size = 300
            self.label_color = 0
            self.erase_mode = True
            self.scroll_speed = 5
            self.border = 50

        if not self.erase_mode:
            self.UI.EraserBtn.setStyleSheet("background-color: rgb(128, 128, 128); font: 9pt 'Arial';")
        # 使用者預設類別
        self.default_layers.clear()
        csv_layers = list(csv.reader(self.default_classes.splitlines()))
        if len(csv_layers) > 0:
            for i in range(len(csv_layers[0])):
                layer = csv_layers[0][i].replace(" ", "")
                if not layer.isdigit():
                    self.default_layers.append(layer)

        # 列出圖片檔名
        self.FM.get_file_lists(self.UI.action_Show_annotated.isChecked())
        if is_running:
            self.UI.listWidget.addItems(self.FM.image_list)
            self.change_image(0)
        self.total_items = f'{len(self.FM.image_list)} item{"" if len(self.FM.image_list) == 1 else "s"}'
        self.UI.NumOfImageslabel.setText(f' {self.FM.index + 1} / {self.total_items}')

    def key_event(self, e: QKeyEvent):
        """

        :param e:
        :return:
        """
        if self.is_processing:
            return
        key = e.key()
        if key == QtCore.Qt.Key_Plus or key == QtCore.Qt.Key_Equal:
            self.scale_display(self.zoom_scale)
        elif key == QtCore.Qt.Key_Minus:
            self.scale_display(-self.zoom_scale)
        elif key == QtCore.Qt.Key_E:
            self.erase_mode_on()
        elif key == QtCore.Qt.Key_Space:
            if not self.erase_mode:
                self.label_color = (self.label_color + 1) % 6
            self.change_brush_color(self.label_color)
        elif key == QtCore.Qt.Key_Left:
            self.change_image(max(self.FM.index - 1, 0))
        elif key == QtCore.Qt.Key_Right:
            self.change_image(min(self.FM.index + 1, len(self.FM.image_list) - 1))
        elif key == QtCore.Qt.Key_Up:
            idx = (self.UI.comboBox.currentIndex() + 1) % self.UI.comboBox.count()
            self.UI.comboBox.setCurrentIndex(idx)
            self.update_layer_state()
        elif key == QtCore.Qt.Key_Down:
            idx = (self.UI.comboBox.currentIndex() - 1) % self.UI.comboBox.count()
            self.UI.comboBox.setCurrentIndex(idx)
            self.update_layer_state()
        if self.m_mode is MMode.Painting and self.paint_mode == PMode.Select:
            # 多邊形填色
            if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
                self.m_mode = MMode.Neutral
                self.painter = QPainter(self.pixmap_mask[self.UI.comboBox.currentText()])
                self.painter.setPen(QPen(label_colors[self.label_color]))
                self.painter.setBrush(QBrush(label_colors[self.label_color]))
                self.painter.setCompositionMode(
                    QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
                )
                self.painter.drawPolygon(QPolygonF(self.selections_pnt))
                self.painter.end()
                self.update_mask(layer_highlight=True)
                if self.display_line.scene() == self.scene:
                    self.scene.removeItem(self.display_line)
                if self.display_sel.scene() == self.scene:
                    self.scene.removeItem(self.display_sel)
                self.selections_pnt.clear()
                self.BM.unsaved_actions += 1
                self.BM.push(self.UI.comboBox.currentText(), self.pixmap_mask[self.UI.comboBox.currentText()])
            elif key == QtCore.Qt.Key_Escape:
                self.m_mode = MMode.Neutral
                if self.display_line.scene() == self.scene:
                    self.scene.removeItem(self.display_line)
                if self.display_sel.scene() == self.scene:
                    self.scene.removeItem(self.display_sel)
                self.selections_pnt.clear()

    def mouse_wheel_event(self, e: QWheelEvent):
        """

        :param e:
        :return:
        """
        delta: Union[QtCore.QPoint, float] = e.pixelDelta()
        if delta is None or delta.y() == 0:
            delta = e.angleDelta() / 10
        modifiers = int(e.modifiers())

        if modifiers and modifiers & MOD_MASK == modifiers:
            keyname = QKeySequence(modifiers).toString()
            if keyname == "Ctrl+":
                oldpos = self.UI.graphicsView.mapToScene(e.pos())
                self.scale_display(delta.y() * 0.01)
                newpos = self.UI.graphicsView.mapToScene(e.pos())
                deltapos = newpos - oldpos
                self.UI.graphicsView.translate(deltapos.x(), deltapos.y())
            if keyname == "Ctrl+Shift+":
                value = self.UI.BrushSizeSlider.value() + delta.y()
                self.UI.BrushSizeSlider.setValue(value)
            if keyname == "Shift+":
                delta *= self.scroll_speed
                value = self.UI.graphicsView.horizontalScrollBar().value() + delta.y()
                self.UI.graphicsView.horizontalScrollBar().setValue(value)
        else:
            delta *= self.scroll_speed
            value = self.UI.graphicsView.verticalScrollBar().value() + delta.y()
            self.UI.graphicsView.verticalScrollBar().setValue(value)

        if self.paint_mode == PMode.Brush:
            # Update cursor position
            r = int(self.brush_size / 2)
            curr_pos = self.UI.graphicsView.mapToScene(e.pos())
            curr_pos.setX(curr_pos.x() - r)
            curr_pos.setY(curr_pos.y() - r)
            self.brush_cursor.setPos(curr_pos)

    # 開始繪圖
    def start_paint(self, e: QMouseEvent):
        """

        :param e:
        :return:
        """
        if self.layer_hidden[self.UI.comboBox.currentText()] is QtCore.Qt.Checked:
            return
        self.m_mode = MMode.Painting
        r = int(self.brush_size / 2)
        curr_pos = self.UI.graphicsView.mapToScene(e.pos())
        if self.paint_mode == PMode.Brush:
            self.painter = QPainter(self.pixmap_mask[self.UI.comboBox.currentText()])
            p = self.painter.pen()
            p.setColor(label_colors[self.label_color])
            self.painter.setPen(p)
            self.painter.setBrush(QBrush(label_colors[self.label_color]))

            self.painter.setCompositionMode(
                QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
            )
            self.painter.drawEllipse(curr_pos.x() - r, curr_pos.y() - r, self.brush_size, self.brush_size)
        elif self.paint_mode is PMode.Select:
            self.selections_pnt.append(curr_pos)
            self.draw_polygon_selection()

    # 結束繪圖
    def end_paint(self):
        """

        :return:
        """
        if self.paint_mode == PMode.Brush:
            self.update_mask()
            self.m_mode = MMode.Neutral
            self.BM.unsaved_actions += 1
            self.painter.end()
            self.BM.push(self.UI.comboBox.currentText(), self.pixmap_mask[self.UI.comboBox.currentText()])

    def mouse_press(self, e: QMouseEvent):
        """

        :param e:
        :return:
        """
        if e.button() == QtCore.Qt.LeftButton and self.m_mode is not MMode.Grabing:
            for item in self.scene.items():
                if isinstance(item, QGraphicsSimpleTextItem):
                    self.scene.removeItem(item)
            self.start_paint(e)
        elif e.button() == QtCore.Qt.RightButton and self.m_mode is MMode.Neutral:
            self.m_mode = MMode.Grabing
            self.UI.graphicsView.viewport().setCursor(QCursor(QtCore.Qt.ClosedHandCursor))
            self.prev_pos = e.pos()

    def mouse_release(self, e: QMouseEvent):
        """

        :param e:
        :return:
        """
        if e.button() == QtCore.Qt.LeftButton and self.m_mode is MMode.Painting:
            self.end_paint()
        elif e.button() == QtCore.Qt.RightButton and self.m_mode is MMode.Grabing:
            self.m_mode = MMode.Neutral
            cursor_type = QtCore.Qt.ArrowCursor if self.paint_mode is PMode.Select else QtCore.Qt.CrossCursor
            self.UI.graphicsView.viewport().setCursor(QCursor(cursor_type))

    # 滑鼠游標在繪圖區移動
    def mouse_movement(self, e: QMouseEvent):
        """

        :param e:
        :return:
        """
        r = int(self.brush_size / 2)
        mappos = self.UI.graphicsView.mapToScene(e.pos())
        curr_x, curr_y = mappos.x() - r, mappos.y() - r
        if self.m_mode is MMode.Painting:
            if self.paint_mode == PMode.Brush:
                self.painter.setCompositionMode(
                    QPainter.CompositionMode_Clear if self.erase_mode else QPainter.CompositionMode_Source
                )
                self.painter.drawEllipse(curr_x, curr_y, self.brush_size, self.brush_size)
                self.update_mask()
            elif self.paint_mode == PMode.Select:
                top = len(self.selections_pnt) - 1
                ax, ay = self.selections_pnt[top].x(), self.selections_pnt[top].y()
                if self.display_line is not None and self.display_line.scene() == self.scene:
                    self.scene.removeItem(self.display_line)
                curr_scale = self.UI.graphicsView.viewportTransform().m11()
                self.display_line = self.scene.addLine(ax, ay, mappos.x(), mappos.y(),
                                                       QPen(QColor(255, 255, 0, 255), 5 / curr_scale))
        elif self.m_mode is MMode.Grabing:
            delta: QPoint = -(e.pos() - self.prev_pos)
            dx = self.UI.graphicsView.horizontalScrollBar().value() + delta.x()
            dy = self.UI.graphicsView.verticalScrollBar().value() + delta.y()
            self.UI.graphicsView.horizontalScrollBar().setValue(dx)
            self.UI.graphicsView.verticalScrollBar().setValue(dy)
            self.prev_pos = e.pos()

        if self.paint_mode == PMode.Brush:
            self.brush_cursor.setPos(QtCore.QPoint(curr_x, curr_y))

    # 滑鼠進入 viewport
    def mouse_enter_viewport(self, e: QMouseEvent):
        if self.paint_mode is PMode.Brush:
            self.brush_cursor.show()

    # 滑鼠離開 viewport
    def mouse_leave_viewport(self, e: QMouseEvent):
        self.brush_cursor.hide()

    # 調整顯示大小
    def scale_display(self, value: float):
        """

        :param value:
        :return:
        """
        # Noise removal
        if abs(value) < 0.01:
            return

        new_scale = 1 + max(min(value, self.zoom_scale), -self.zoom_scale)
        tgt_scale = self.UI.graphicsView.viewportTransform().m11() * new_scale
        if tgt_scale > self.zoom_max:
            new_scale = 1
        self.UI.graphicsView.scale(new_scale, new_scale)
        t = self.UI.graphicsView.viewportTransform()
        if t.m31() >= self.border and t.m32() >= self.border:
            self.scale_to_fit()
        if self.m_mode is MMode.Painting and self.paint_mode is PMode.Select:
            self.draw_polygon_selection()

    # 調整 viewport 符合圖片大小
    def scale_to_fit(self, e: QWheelEvent = None):
        """

        :param e:
        :return:
        """
        if self.display_img is not None:
            rect = self.UI.graphicsView.scene().sceneRect()
            self.UI.graphicsView.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    # 切換圖片
    def change_image(self, _index: int):
        """

        :param _index:
        :return:
        """
        if self.is_processing:
            return
        self.is_processing = True
        self.UI.FuncBtn1.setDisabled(True)
        self.UI.FuncBtn2.setDisabled(True)

        if self.save_annotation() == 3:
            self.is_processing = False
            self.UI.FuncBtn1.setDisabled(False)
            self.UI.FuncBtn2.setDisabled(False)
            return

        self.FM.index = _index
        self.UI.listWidget.setCurrentRow(_index)
        self.UI.NumOfImageslabel.setText(f' {self.FM.index + 1} / {self.total_items}')
        retrived_name = re.sub("\\[([0-9]+)\\] ", "", self.FM.image_list[_index])
        self.pixmap_img = QPixmap(f'{self.FM.image_dir}/{retrived_name}')

        if self.display_img is None:
            self.display_img = self.scene.addPixmap(self.pixmap_img)
        else:
            self.display_img.setPixmap(self.pixmap_img)

        # 移除類別標籤
        for item in self.scene.items():
            if isinstance(item, QGraphicsSimpleTextItem):
                self.scene.removeItem(item)

        self.draw_annotations(_index)
        b_top = -self.border
        b_btm = 2 * self.border
        self.scene.setSceneRect(
            QtCore.QRectF(b_top, b_top, self.pixmap_img.width() + b_btm, self.pixmap_img.height() + b_btm)
        )
        self.BM.renew_buffer(self.pixmap_mask)
        self.update_mask()
        self.UI.graphicsView.fitInView(self.display_img, QtCore.Qt.KeepAspectRatio)
        self.main_window.setWindowTitle(f'Mask Editor -- {retrived_name}')

        self.is_processing = False
        self.UI.FuncBtn1.setDisabled(False)
        self.UI.FuncBtn2.setDisabled(False)

    def refresh_masks(self):
        """

        :return:
        """
        if self.save_annotation() == 3:
            return
        curr_class = self.UI.comboBox.currentText()
        self.draw_annotations(self.FM.index)
        self.UI.comboBox.setCurrentText(curr_class)
        self.update_mask(layer_highlight=True)
        self.BM.unsaved_actions = 0

    def draw_annotations(self, _index):
        """

        :param _index:
        :return:
        """
        # blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
        blank = QPixmap(self.pixmap_img.size())
        blank.fill(Colors.BLANK)
        self.pixmap_mask.clear()
        for key, item in self.display_mask.items():
            self.scene.removeItem(item)
        self.display_mask.clear()
        self.layer_hidden.clear()

        # 先加入使用者設定預設圖層
        for layer in self.default_layers:
            self.pixmap_mask[layer] = blank.copy()
        # 利用 label 檔的輪廓資訊繪製遮罩
        if len(self.FM.annotations) > 0:
            try:
                class_counter: dict = {}
                f_name = re.sub("\\[([0-9]+)\\] ", "", self.FM.image_list[_index])
                f_size = os_path.getsize(f'{self.FM.image_dir}/{f_name}')
                f_name = f'{f_name}{f_size}'
                a = self.FM.annotations[f_name]
                # polygons = [r['shape_attributes'] for r in a['regions']]

                self.cidx = 0
                result: dict = {}
                threads: list = []
                for r in a['regions']:
                    t = Thread(target=self.process_region(r, result))
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join()
                threads.clear()

                for key, val in result.items():
                    try:
                        self.pixmap_mask[key]
                    except KeyError:
                        self.pixmap_mask[key] = blank.copy()

                    class_counter[key] = len(val)
                    t = Thread(target=paint_regions_by_class(self.pixmap_mask[key], val))
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()

                msg = f"{len(a['regions'])} region(s) loaded. | "
                for key, val in class_counter.items():
                    msg += f"{val} {key}(s), "
                self.UI.statusbar.showMessage(msg[:len(msg) - 2])

            except KeyError:
                self.UI.statusbar.showMessage('No region annotated in this image')
        # 若沒有資料導入 創建預設類別圖層
        if len(self.pixmap_mask) == 0:
            self.pixmap_mask['object'] = blank
        # 更新 Class 下拉式清單
        self.UI.comboBox.clear()
        for key, val in self.pixmap_mask.items():
            self.UI.comboBox.addItem(key)

    def process_region(self, r, res: dict):
        """

        :param r:
        :param res:
        :return:
        """
        area: QPolygon = QPolygon()
        p = r['shape_attributes']
        for i in range(len(p['all_points_x'])):
            area.append(QPoint(p['all_points_x'][i], p['all_points_y'][i]))

        try:
            paint_color = label_colors[nameref[r['region_attributes']['Color']]]
        except KeyError:
            paint_color = label_colors[self.cidx]
            self.cidx = (self.cidx + 1) % 6

        classname = next(iter(r['region_attributes'].values()))
        try:
            res[classname]
        except KeyError:
            res[classname] = []
        # 顯示列別標籤
        if self.show_tag:
            tag = self.scene.addSimpleText(classname, QFont("Cursive", self.tag_size, QFont.Bold))
            tag.setPos(area.last())
            tag.setPen(QPen(QColor(0, 0, 0), self.tag_size / 15))
            tag.setBrush(Colors.WHITE)
            tag.setZValue(1)
        res[classname].append([paint_color, area])

    # 更新顯示遮罩
    def update_mask(self, layer_highlight: bool = False):
        """

        :return:
        """
        if self.m_mode is MMode.Painting:
            classname = self.UI.comboBox.currentText()
            pixmap = self.pixmap_mask[classname]
            try:
                self.display_mask[classname].setPixmap(pixmap)
            except KeyError:
                self.display_mask[classname] = self.scene.addPixmap(pixmap)
                self.display_mask[classname].setOpacity(0.5)
                self.layer_hidden[classname] = QtCore.Qt.Unchecked
        else:
            classname = self.UI.comboBox.currentText()
            threads = []
            for key, val in self.pixmap_mask.items():
                t = Thread(target=self.set_masks(key, val, classname, layer_highlight))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

    def set_masks(self, key: str, val: QPixmap, classname: str, layer_highlight: bool):
        if not layer_highlight or key == classname:
            pixmap = val
        else:
            pixmap: QPixmap = QPixmap(val.size())
            pixmap.fill(Colors.SANDYBROWN)
            pixmap.setMask(val.createMaskFromColor(Colors.BLANK))

        try:
            self.display_mask[key].setPixmap(pixmap)
        except KeyError:
            self.display_mask[key] = self.scene.addPixmap(pixmap)
            self.display_mask[key].setOpacity(0.5)
            self.layer_hidden[key] = QtCore.Qt.Unchecked

    # 繪製多邊形選擇外框
    def draw_polygon_selection(self):
        """

        :return:
        """
        if self.display_sel is not None and self.display_sel.scene() == self.scene:
            self.scene.removeItem(self.display_sel)
        my_path = QPainterPath()
        my_path.addPolygon(QPolygonF(self.selections_pnt))
        my_path.closeSubpath()
        curr_scale = self.UI.graphicsView.viewportTransform().m11()
        self.display_sel = self.scene.addPath(my_path, QPen(QColor(255, 255, 0, 255), 5 / curr_scale))

    # 復原動作
    def undo_changes(self):
        """

        :return:
        """
        classname = self.UI.comboBox.currentText()
        pixmap = self.BM.undo_changes(classname)
        if pixmap is not None:
            self.pixmap_mask[classname] = pixmap
            self.update_mask(layer_highlight=True)

    # 重做動作
    def redo_changes(self):
        """

        :return:
        """
        classname = self.UI.comboBox.currentText()
        pixmap = self.BM.redo_changes(classname)
        if pixmap is not None:
            self.pixmap_mask[classname] = pixmap
            self.update_mask(layer_highlight=True)

    # 改變筆刷大小
    def change_brush_size(self):
        """

        :return:
        """
        if self.paint_mode == PMode.Brush:
            value = self.UI.BrushSizeSlider.value()
            self.brush_size = value
            self.gen_brush()

    # 改變筆刷顏色
    def change_brush_color(self, index: int):
        """

        :param index:
        :return:
        """
        self.UI.ColorBtn1.setStyleSheet("background-color: rgb(128, 0, 0);")
        self.UI.ColorBtn2.setStyleSheet("background-color: rgb(0, 128, 0);")
        self.UI.ColorBtn3.setStyleSheet("background-color: rgb(0, 0, 128);")
        self.UI.ColorBtn4.setStyleSheet("background-color: rgb(128, 128, 0);")
        self.UI.ColorBtn5.setStyleSheet("background-color: rgb(128, 0, 128);")
        self.UI.ColorBtn6.setStyleSheet("background-color: rgb(0, 128, 128);")

        if self.erase_mode:
            self.erase_mode = False
            self.UI.EraserBtn.setStyleSheet("background-color: rgb(128, 128, 128); font: 9pt 'Arial';")
        self.label_color = index
        if index == 0:
            self.UI.ColorBtn1.setStyleSheet("background-color: rgb(255, 0, 0);")
        elif index == 1:
            self.UI.ColorBtn2.setStyleSheet("background-color: rgb(0, 255, 0);")
        elif index == 2:
            self.UI.ColorBtn3.setStyleSheet("background-color: rgb(0, 0, 255);")
        elif index == 3:
            self.UI.ColorBtn4.setStyleSheet("background-color: rgb(255, 255, 0);")
        elif index == 4:
            self.UI.ColorBtn5.setStyleSheet("background-color: rgb(255, 0, 255);")
        elif index == 5:
            self.UI.ColorBtn6.setStyleSheet("background-color: rgb(0, 255, 255);")
        self.gen_brush()

    # 改變底圖亮度
    def change_photo_brightness(self):
        """

        :return:
        """
        value = self.UI.brightnessSlider.value() / 100
        self.display_img.setOpacity(value)
        if value < 0.5:
            self.display_mask[self.UI.comboBox.currentText()].setOpacity(1 - value)

    # 產生筆刷
    def gen_brush(self):
        """

        :return:
        """
        # if self.paint_mode is not PMode.Brush:
        #     return
        curr_pos = QPoint(0, 0)
        if self.brush_cursor is not None:
            curr_pos = self.brush_cursor.pos()
            self.scene.removeItem(self.brush_cursor)
        if self.erase_mode:
            brush_color = Colors.WHITE
        else:
            brush_color = label_colors[self.label_color]
        pen = QPen(brush_color)
        self.brush_cursor = self.scene.addEllipse(
            QtCore.QRectF(0, 0, self.brush_size, self.brush_size),
            pen,
            QBrush(brush_color)
        )
        self.brush_cursor.setOpacity(0.5)
        self.brush_cursor.setPos(curr_pos)
        if not self.UI.graphicsView.underMouse() or self.paint_mode is not PMode.Brush:
            self.brush_cursor.hide()

    # 擦去模式開關
    def erase_mode_on(self):
        """

        :return:
        """
        self.erase_mode = True
        self.UI.EraserBtn.setStyleSheet("background-color: rgb(255, 255, 255); font: 9pt 'Arial';")
        if self.label_color == 0:
            self.UI.ColorBtn1.setStyleSheet("background-color: rgb(128, 0, 0);")
        elif self.label_color  == 1:
            self.UI.ColorBtn2.setStyleSheet("background-color: rgb(0, 128, 0);")
        elif self.label_color  == 2:
            self.UI.ColorBtn3.setStyleSheet("background-color: rgb(0, 0, 128);")
        elif self.label_color  == 3:
            self.UI.ColorBtn4.setStyleSheet("background-color: rgb(128, 128, 0);")
        elif self.label_color  == 4:
            self.UI.ColorBtn5.setStyleSheet("background-color: rgb(128, 0, 128);")
        elif self.label_color  == 5:
            self.UI.ColorBtn6.setStyleSheet("background-color: rgb(0, 128, 128);")
        self.gen_brush()

    # 離開程式
    def on_exit(self, e):
        """

        :param e:
        :return:
        """
        if self.BM.unsaved_actions > 0:
            self.save_annotation()

        self.config["GeneralSettings"] = {'ImageDir': self.FM.image_dir,  # 圖片資料夾
                                          'DefaultClasses': self.default_classes,
                                          'ZoomScale': str(self.zoom_scale),
                                          'ZoomMaxScale': str(self.zoom_max),
                                          'InvertScroll': 'False' if self.scroll_speed < 0 else 'True',
                                          'BorderInPixels': self.border,
                                          'ShowClassNameTag': int(self.show_tag),
                                          'ClassNameTagFontSize': self.tag_size
                                          }
        self.config["WorkingState"] = {'WorkingImg': str(self.FM.index),
                                       'BrushSize': str(self.brush_size),
                                       'BrushColor': self.label_color,
                                       'Erasemode': int(self.erase_mode),
                                       'ShowAnnotated': int(self.UI.action_Show_annotated.isChecked())
                                       }
        with open('settings.ini', 'w') as file:
            self.config.write(file)

    def save_mask(self):
        """

        :return:
        """
        self.FM.save_mask(self.pixmap_mask)

    def save_annotation(self):
        """

        :return:
        """
        if self.BM.unsaved_actions != 0:
            return self.FM.save_annotation(self.pixmap_mask)

    def delete_mask(self):
        """

        :return:
        """
        self.FM.delete_mask()

    def change_settings(self):
        """

        :return:
        """
        dialog_settings = QDialog()
        ui = Ui_DialogSettings()
        ui.setupUi(dialog_settings)

        ui.lineEdit.setText(self.FM.image_dir)
        ui.lineEdit_2.setText(self.default_classes)
        ui.lineEdit_3.setText(str(self.zoom_scale))
        ui.lineEdit_4.setText(str(self.zoom_max))
        ui.lineEdit_5.setText(str(self.border))
        ui.lineEdit_6.setText(str(self.tag_size))
        ui.checkBox_2.setChecked(self.show_tag)

        res = dialog_settings.exec()
        if res == QDialog.Accepted:
            if not ui.lineEdit_2.text().isdigit():
                self.default_classes = ui.lineEdit_2.text()
                # 使用者預設類別
                self.default_layers.clear()
                csv_layers = list(csv.reader(self.default_classes.splitlines()))
                if len(csv_layers) > 0:
                    for i in range(len(csv_layers[0])):
                        layer = csv_layers[0][i].replace(" ", "")
                        if not layer.isdigit():
                            self.default_layers.append(layer)

            if ui.lineEdit_3.text().isdigit():
                self.zoom_scale = max(min(float(ui.lineEdit_3.text()), 2), 0.01)
            if ui.lineEdit_4.text().isdigit():
                self.zoom_max = max(min(float(ui.lineEdit_4.text()), 10), 2)
            if ui.lineEdit_5.text().isdigit():
                self.border = max(min(int(ui.lineEdit_5.text()), 1200), 10)
            if ui.lineEdit_6.text().isdigit():
                self.tag_size = max(min(int(ui.lineEdit_6.text()), 48), 8)
            self.show_tag = ui.checkBox_2.isChecked()
            # update changes
            self.change_image(self.FM.index)

    def add_class(self):
        """

        :return:
        """
        dialog_line_edit = QDialog()
        ui = Ui_DialogLineEdit()
        ui.setupUi(dialog_line_edit)
        dialog_line_edit.setWindowTitle('Add Class')
        ui.label.setText('Please enter the name of the new class')
        res = dialog_line_edit.exec()

        newclass = ui.lineEdit.text().replace(" ", "")

        if res == QDialog.Accepted and newclass != "":
            if self.UI.comboBox.findText(newclass) != -1:
                QMessageBox.about(self.FM.dialog_root,
                                  "Redefining class",
                                  f'Class "{newclass}" already exists'
                                  )
                return
            elif newclass.isdigit():
                QMessageBox.about(self.FM.dialog_root,
                                  "Class name invalid",
                                  "Class name should not be a number"
                                  )
                return

            # blank = QImage(self.pixmap_img.width(), self.pixmap_img.height(), QImage.Format_ARGB32)
            blank = QPixmap(self.pixmap_img.size())
            blank.fill(Colors.BLANK)

            self.pixmap_mask[newclass] = blank
            self.BM.push(newclass, self.pixmap_mask[newclass])
            self.UI.comboBox.addItem(newclass)
            self.layer_hidden[newclass] = QtCore.Qt.Unchecked
            self.UI.comboBox.setCurrentText(newclass)
            self.update_layer_state()
            if ui.checkBox.isChecked():
                self.default_classes += f",{newclass}"
                self.default_layers.append(newclass)

    def change_paint_mode(self):
        """

        :return:
        """
        if self.UI.action_Select_Polygon.isChecked():
            self.paint_mode = PMode.Select
            self.brush_cursor.hide()
            self.UI.graphicsView.viewport().setCursor(QCursor(QtCore.Qt.ArrowCursor))
        else:
            self.paint_mode = PMode.Brush
            # self.gen_brush()
            self.brush_cursor.show()
            self.UI.graphicsView.viewport().setCursor(QCursor(QtCore.Qt.CrossCursor))

    def update_layer_state(self):
        curr_class = self.UI.comboBox.currentText()
        self.UI.HideLayerCheckBox.setCheckState(self.layer_hidden[curr_class])
        self.update_mask(layer_highlight=True)

    def hide_layer(self):
        curr_class = self.UI.comboBox.currentText()
        if self.UI.HideLayerCheckBox.isChecked():
            self.display_mask[curr_class].hide()
            self.layer_hidden[curr_class] = QtCore.Qt.Checked
        else:
            self.display_mask[curr_class].show()
            self.layer_hidden[curr_class] = QtCore.Qt.Unchecked
