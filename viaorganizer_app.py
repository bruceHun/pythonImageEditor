from PyQt5.QtGui import QPixmap, QPolygon, QPen, QPainterPath, QPolygonF, QWheelEvent, QTransform, QKeyEvent, QColor, \
    QKeySequence, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QTableWidgetItem, QTableWidget, QHeaderView, QMessageBox, \
    QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal, QObject

from viaorganizer import Ui_MainWindow
from anno_info import Ui_Form
from PyQt5 import QtWidgets
from typing import Union
from configparser import ConfigParser, NoOptionError, NoSectionError
from copy import deepcopy
import json

colors = {
    'Red': QColor(255, 0, 0),
    'Green': QColor(0, 255, 0),
    'Blue': QColor(0, 0, 255),
    'Yellow': QColor(255, 255, 0),
    'Fuchsia': QColor(255, 0, 255),
    'Aqua': QColor(0, 255, 255),
}


class ViaOrganizer:

    def __init__(self, _ui: Ui_MainWindow, _win: QtWidgets.QMainWindow):
        self.UI: Ui_MainWindow = _ui
        self.Form: list = [None, None]
        self.FormPreview: Union[QPixmap, None] = None
        self.win: QtWidgets.QMainWindow = _win
        self.directory: str = ''
        self.json_in = [{}, {}]
        self.sub = [None, None]
        self.scene: Union[QtWidgets.QGraphicsScene, None] = None
        self.mark: list = []
        self.config: Union[ConfigParser, None] = None
        self.zoom: float = 1.0
        self.on_form: int = 1
        self.loading_attribute: bool = False
        self.curr_idx: list = [0, 0]

    def init(self):
        self.config = ConfigParser()
        self.config.optionxform = str
        try:
            settings = open("viaorg_settings.ini", "r")
            settings.close()
            self.config.read("viaorg_settings.ini")
            self.directory = self.config.get("GeneralSettings", 'ImageDir')
            f_name = [self.config.get("GeneralSettings", 'Destination'), self.config.get("GeneralSettings", 'Source')]
            self.curr_idx[0] = int(self.config.get("WorkingState", "SrcIndex"))
            self.curr_idx[1] = int(self.config.get("WorkingState", "DesIndex"))
        except (FileNotFoundError, NoOptionError, NoSectionError):
            # 指定圖片資料夾
            self.directory = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
            # 開 JSON 檔
            res1, f_type = QFileDialog.getOpenFileName(caption='Select Destination file', filter="JSON files (*.json)")
            res2, f_type = QFileDialog.getOpenFileName(caption='Select Source file', filter="JSON files (*.json)")
            f_name = [res1, res2]

            self.config["GeneralSettings"] = {'ImageDir': self.directory,  # 圖片資料夾
                                              'Destination': f_name[0],
                                              'Source': f_name[1]
                                              }
            self.config["WorkingState"] = {'SrcIndex': "0",
                                           'DesIndex': "0"
                                           }
            with open('viaorg_settings.ini', 'w') as file:
                self.config.write(file)

        for i in range(2):
            with open(f_name[i], 'r') as json_file:
                self.json_in[i] = json.load(json_file)
            print(len(self.json_in[i]))
        for i in [1, 0]:
            self.sub[i] = QtWidgets.QMdiSubWindow(flags=Qt.CustomizeWindowHint)
            form = QtWidgets.QWidget()
            self.Form[i]: Ui_Form = Ui_Form()
            self.Form[i].setupUi(form)
            self.sub[i].setWidget(form)
            self.UI.mdiArea.addSubWindow(self.sub[i])
            title = 'Source' if i == 1 else 'Destination'
            self.sub[i].setWindowTitle(title)
            self.sub[i].show()

        self.UI.mdiArea.tileSubWindows()
        # Populate ListWidget
        for i in range(2):
            for j, filename in enumerate(self.json_in[i]):
                # self.UI.listWidget.addItem(filename)
                self.Form[i].listWidget.addItem(filename)
            if self.Form[i].listWidget.count() > 0:
                self.Form[i].listWidget.setCurrentRow(self.curr_idx[i])

        f1: Ui_Form = self.Form[0]
        f2: Ui_Form = self.Form[1]
        f2.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        f2.listWidget.setDefaultDropAction(Qt.CopyAction)
        f2.listWidget_2.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        f2.listWidget_2.setDefaultDropAction(Qt.CopyAction)

        self.scene = QtWidgets.QGraphicsScene()
        self.UI.graphicsView.setScene(self.scene)

        self.update_preview(0)

        self.UI.graphicsView.wheelEvent = self.wheel_event
        self.win.closeEvent = self.on_exit
        f1.listWidget.dropEvent = self.drop_annotation_src_to_des
        f1.listWidget_2.dropEvent = self.drop_region_src_to_des
        f1.listWidget.keyPressEvent = self.f1_anno_key_event
        f1.listWidget_2.keyPressEvent = self.f1_region_key_event

        # UI 功能連結
        self.UI.action_Save.triggered.connect(self.save_file)
        self.UI.action_Delete.triggered.connect(self.delete_selected_annotations)
        self.UI.actionZoom_In.triggered.connect(lambda: self.zoom_preview(0.1))
        self.UI.actionZoom_Out.triggered.connect(lambda: self.zoom_preview(-0.1))
        self.UI.actionPrevAnnotation.triggered.connect(lambda: self.change_annotation(-1))
        self.UI.actionNextAnnotation.triggered.connect(lambda: self.change_annotation(1))
        self.UI.actionPrev_Region.triggered.connect(lambda: self.change_region(-1))
        self.UI.actionNext_Region.triggered.connect(lambda: self.change_region(1))
        self.UI.actionSwitch_Tab.triggered.connect(self.UI.mdiArea.activateNextSubWindow)
        # self.UI.actionConvert_to_simple_name.triggered.connect(self.convert_to_simple_naming)
        self.UI.actionConvert_to_VIA_naming.triggered.connect(self.convert_to_VIA_naming)
        self.Form[0].listWidget.currentRowChanged.connect(lambda: self.update_preview(0))
        self.Form[0].listWidget.itemClicked.connect(lambda: self.update_preview(0))
        self.Form[0].listWidget_2.currentRowChanged.connect(lambda: self.show_attribute(0))
        self.Form[0].listWidget_2.itemClicked.connect(lambda: self.show_attribute(0))
        self.Form[0].tableWidget.cellChanged.connect(self.edit_attribute)
        self.Form[1].listWidget.currentRowChanged.connect(lambda: self.update_preview(1))
        self.Form[1].listWidget.itemClicked.connect(lambda: self.update_preview(1))
        self.Form[1].listWidget_2.currentRowChanged.connect(lambda: self.show_attribute(1))
        self.Form[1].listWidget_2.itemClicked.connect(lambda: self.show_attribute(1))

    # 更新預覽
    def update_preview(self, idx: int):
        self.on_form = idx
        form = self.Form[idx]
        curr_text = self.Form[idx].listWidget.currentItem().text()
        f_name = f"{self.directory}/{self.json_in[idx][curr_text]['filename']}"
        if self.FormPreview is None:
            self.FormPreview = self.scene.addPixmap(QPixmap(f_name))
        else:
            self.FormPreview.setPixmap(QPixmap(f_name))

        # Populate ListWidget
        form.listWidget_2.clear()
        # self.Form[idx].listWidget_3.clear()
        form.tableWidget.clear()
        for i, region in enumerate(self.json_in[idx][curr_text]['regions']):
            # print(i, region['region_attributes'])
            # self.UI.listWidget.addItem(filename)
            self.Form[idx].listWidget_2.addItem(str(i))
        form.listWidget_2.setCurrentRow(-1)

        self.UI.graphicsView.fitInView(self.FormPreview, Qt.KeepAspectRatio)
        self.zoom = self.UI.graphicsView.viewportTransform().m11()

        for mk in self.mark:
            self.scene.removeItem(mk)
        self.mark.clear()
        for curr_idx in range(form.listWidget_2.count()):

            p = self.json_in[idx][curr_text]['regions'][curr_idx]['shape_attributes']
            points = [QPointF(p['all_points_x'][i], p['all_points_y'][i]) for i in range(len(p['all_points_x']))]
            area: QPolygonF = QPolygonF(points)
            path = QPainterPath()
            path.addPolygon(area)
            path.closeSubpath()
            try:
                cid = self.json_in[idx][curr_text]['regions'][curr_idx]['region_attributes']['Color']
                color = colors[cid]
            except KeyError:
                color = Qt.yellow
            self.mark.append(self.scene.addPath(path, QPen(color, 5)))

    def show_attribute(self, idx: int):
        if self.on_form != idx:
            self.update_preview(idx)
        curr_idx = self.Form[idx].listWidget_2.currentRow()
        if curr_idx < 0:
            # self.Form[idx].listWidget_3.addItem('N/A')
            return
        curr_text = self.Form[idx].listWidget.currentItem().text()
        self.UI.graphicsView.fitInView(self.mark[curr_idx], Qt.KeepAspectRatio)
        self.zoom = self.UI.graphicsView.viewportTransform().m11()
        # Populate ListWidget
        # self.Form[idx].listWidget_3.clear()
        table: QTableWidget = self.Form[idx].tableWidget
        table.clear()
        table.setHorizontalHeaderLabels(['Attr', 'Value'])
        r = self.json_in[idx][curr_text]['regions'][curr_idx]['region_attributes']
        table.setRowCount(len(r))
        table.setColumnCount(2)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.Form[idx].listWidget_2.connect(table, pyqtSignal("itemClicked(QTableWidgetItem *)"), self.edit_attribute)
        self.loading_attribute = True
        for i, attr in enumerate(r):
            # self.Form[idx].listWidget_3.addItem(f"{attr}: {r[attr]}")
            table.setItem(i, 0, QTableWidgetItem(attr))
            table.setItem(i, 1, QTableWidgetItem(r[attr]))
        self.loading_attribute = False
        table.show()

    def wheel_event(self, e: QWheelEvent):
        keyname = QKeySequence(e.modifiers()).toString()
        if keyname == "Ctrl+":
            delta: Union[QPoint, float] = e.pixelDelta()
            # if delta is None or delta.y() == 0:
            #     delta = e.angleDelta() / 10
            delta /= 10
            self.zoom_preview(delta.y())

    def drop_annotation_src_to_des(self, e: QDropEvent):
        f1: Ui_Form = self.Form[0]
        f2: Ui_Form = self.Form[1]
        src: QListWidget = e.source()
        in_text = src.currentItem().text()
        if e.source() is f2.listWidget:
            if len(f1.listWidget.findItems(in_text, Qt.MatchExactly)) > 0:
                result = QMessageBox.question(self.UI.centralwidget,
                                              "Override annotation?",
                                              "Annotations for this image already exists.\n"
                                              "Are your sure you want to override them?\n"
                                              "\n[Yes] saves your changes"
                                              "\n[No]  discards your changes",
                                              QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.No:
                    return
            else:
                super(QListWidget, f1.listWidget).dropEvent(e)

            self.json_in[0][in_text] = deepcopy(self.json_in[1][in_text])
            print('drop accepted')
            self.update_preview(0)
        else:
            print('drop denied')

    def drop_region_src_to_des(self, e: QDropEvent):
        f1: Ui_Form = self.Form[0]
        f2: Ui_Form = self.Form[1]
        src: QListWidget = e.source()
        src_text = f2.listWidget.currentItem().text()
        des_text = f1.listWidget.currentItem().text()
        new_data = deepcopy(self.json_in[1][src_text]['regions'][src.currentRow()])
        self.json_in[0][des_text]['regions'].append(new_data)
        self.update_preview(0)

    def edit_attribute(self, i, j):
        if self.loading_attribute:
            return
        f1: Ui_Form = self.Form[0]
        a = f1.listWidget.currentItem().text()
        r = self.json_in[0][a]['regions']
        idx = f1.listWidget_2.currentRow()
        attr: dict = r[idx]['region_attributes']
        keys = list(attr.keys())
        for idx, key in enumerate(keys):
            if j > 0 and i == idx:
                attr[key] = f1.tableWidget.item(i, j).text()
            elif j == 0 and i == idx:
                attr[f1.tableWidget.item(i, j).text()] = attr.pop(key)
            else:
                tmp = attr.pop(key)
                attr[key] = tmp

    def zoom_preview(self, delta_y: float):
        m: QTransform = QTransform()
        self.zoom = max(min(self.zoom + delta_y, 10.0), 0.01)
        m.scale(self.zoom, self.zoom)
        # print(delta_y, self.zoom)
        self.UI.graphicsView.setTransform(m)

    def change_annotation(self, step: int):
        idx = 0 if self.UI.mdiArea.activeSubWindow() == self.sub[0] else 1
        form: Ui_Form = self.Form[idx]
        curr_row = form.listWidget.currentRow()
        end = form.listWidget.count() - 1
        form.listWidget.setCurrentRow(max(min(curr_row + step, end), 0))

    def change_region(self, step: int):
        idx = 0 if self.UI.mdiArea.activeSubWindow() == self.sub[0] else 1
        form: Ui_Form = self.Form[idx]
        curr_row = form.listWidget_2.currentRow()
        end = form.listWidget_2.count() - 1
        form.listWidget_2.setCurrentRow(max(min(curr_row + step, end), 0))

    def f1_anno_key_event(self, e: QKeyEvent):
        # super(QListWidget, self.Form[0].listWidget).keyPressEvent(e)
        key = e.key()
        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            self.delete_selected_annotations()

    # 目標資料 region 欄位鍵盤事件
    def f1_region_key_event(self, e: QKeyEvent):
        key = e.key()
        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            self.delete_selected_regions()
        elif key == Qt.Key_Up:
            f1: Ui_Form = self.Form[0]
            f1.listWidget_2.setCurrentRow(max(f1.listWidget_2.currentRow() - 1, 0))
        elif key == Qt.Key_Down:
            f1: Ui_Form = self.Form[0]
            end = f1.listWidget_2.count() - 1
            f1.listWidget_2.setCurrentRow(min(f1.listWidget_2.currentRow() + 1, end))

    # 另存異動後 JSON 檔案
    def save_file(self):
        result = QMessageBox.question(self.UI.centralwidget,
                                      "Save changes?",
                                      "Would you like to save your changes?\n"
                                      "Note: This action cannot be undone.",
                                      QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.Yes:
            json_out = {}
            for i in range(self.Form[0].listWidget.count()):
                filename = self.Form[0].listWidget.item(i).text()
                json_out[filename] = self.json_in[0][filename]

            with open(self.config.get("GeneralSettings", 'Destination'), 'w') as json_file:
                json_file.write(str(json.dumps(json_out)))

    # 刪除選取項目
    def delete_selected_annotations(self):
        print('delete annotations')
        while len(self.Form[0].listWidget.selectedIndexes()) > 0:
            selections = self.Form[0].listWidget.selectedIndexes()
            self.Form[0].listWidget.takeItem(selections[0].row())

    def delete_selected_regions(self):
        print('delete regions')
        f1: Ui_Form = self.Form[0]
        r: list = self.json_in[0][f1.listWidget.currentItem().text()]['regions']
        ridx = f1.listWidget_2.currentRow()
        r.pop(ridx)
        f1.listWidget_2.takeItem(f1.listWidget_2.currentRow())
        self.update_preview(0)

    def convert_to_simple_naming(self):
        json_out = {}
        for i in range(self.Form[0].listWidget.count()):
            in_f_name = self.Form[0].listWidget.item(i).text()
            out_f_name = self.json_in[in_f_name]['filename']
            json_out[out_f_name] = self.json_in[in_f_name]

        self.json_in = json_out
        # Re-Populate ListWidget
        self.Form[0].listWidget.clear()
        for i, filename in enumerate(self.json_in):
            self.Form[0].listWidget.addItem(filename)

    def convert_to_VIA_naming(self):
        json_out = {}
        for i in range(self.Form[0].listWidget.count()):
            in_f_name = self.Form[0].listWidget.item(i).text()
            out_f_name = self.json_in[in_f_name]['filename']
            f_size = self.json_in[in_f_name]['size']
            out_f_name = f'{out_f_name}{f_size}'
            json_out[out_f_name] = self.json_in[in_f_name]

        self.json_in = json_out
        # Re-Populate ListWidget
        self.Form[0].listWidget.clear()
        for i, filename in enumerate(self.json_in):
            self.Form[0].listWidget.addItem(filename)

    def on_exit(self, e):
        self.config["WorkingState"] = {'SrcIndex': str(self.Form[0].listWidget.currentRow()),
                                       'DesIndex': str(self.Form[1].listWidget.currentRow())
                                       }
        with open('viaorg_settings.ini', 'w') as file:
            self.config.write(file)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    organizer = ViaOrganizer(ui, MainWindow)
    MainWindow.show()
    organizer.init()
    sys.exit(app.exec_())
