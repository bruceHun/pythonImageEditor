
from PyQt5.QtGui import QPixmap, QPolygon, QPen, QPainterPath, QPolygonF, QWheelEvent, QTransform, QKeyEvent, QColor, \
    QKeySequence, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QTableWidgetItem, QTableWidget, QHeaderView, QMessageBox, \
    QListWidget
from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal, QObject

from viaorganizer import Ui_MainWindow
from anno_info import Ui_Form
from PyQt5 import QtWidgets
from typing import Union
from configparser import ConfigParser, NoOptionError
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
        self.scene: Union[QtWidgets.QGraphicsScene, None] = None
        self.mark: list = []
        self.config: Union[ConfigParser, None] = None
        self.zoom: float = 1.0
        self.on_form: int = 1

    def init(self):
        self.config = ConfigParser()
        self.config.optionxform = str
        try:
            settings = open("viaorg_settings.ini", "r")
            settings.close()
            self.config.read("viaorg_settings.ini")
            self.directory = self.config.get("GeneralSettings", 'ImageDir')
            f_name = [self.config.get("GeneralSettings", 'Source'), self.config.get("GeneralSettings", 'Destination')]

        except (FileNotFoundError, NoOptionError):
            # 指定圖片資料夾
            self.directory = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
            # 開 JSON 檔
            res1, f_type = QFileDialog.getOpenFileName(caption='Select Destination file', filter="JSON files (*.json)")
            res2, f_type = QFileDialog.getOpenFileName(caption='Select Source file', filter="JSON files (*.json)")
            f_name = [res1, res2]

            self.config["GeneralSettings"] = {'ImageDir': self.directory,  # 圖片資料夾
                                              'Source': f_name[0],
                                              'Destination': f_name[1]
                                              }
            with open('viaorg_settings.ini', 'w') as file:
                self.config.write(file)

        for i in range(2):
            with open(f_name[i], 'r') as json_file:
                self.json_in[i] = json.load(json_file)
            print(len(self.json_in[i]))
        for i in [1, 0]:
            sub = QtWidgets.QMdiSubWindow(flags=Qt.CustomizeWindowHint)
            form = QtWidgets.QWidget()
            self.Form[i]: Ui_Form = Ui_Form()
            self.Form[i].setupUi(form)
            sub.setWidget(form)
            self.UI.mdiArea.addSubWindow(sub)
            title = 'Source' if i == 1 else 'Destination'
            sub.setWindowTitle(title)
            sub.show()

        self.UI.mdiArea.tileSubWindows()
        # Populate ListWidget
        for i in range(2):
            for j, filename in enumerate(self.json_in[i]):
                # self.UI.listWidget.addItem(filename)
                self.Form[i].listWidget.addItem(filename)
            if self.Form[i].listWidget.count() > 0:
                self.Form[i].listWidget.setCurrentRow(0)

        f1: Ui_Form = self.Form[0]
        f2: Ui_Form = self.Form[1]
        f2.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        f2.listWidget.setDefaultDropAction(Qt.CopyAction)
        f2.listWidget_2.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        f2.listWidget_2.setDefaultDropAction(Qt.CopyAction)

        self.scene = QtWidgets.QGraphicsScene()
        self.UI.graphicsView.setScene(self.scene)

        self.update_preview(0)

        self.UI.centralwidget.keyPressEvent = self.key_event
        self.UI.graphicsView.wheelEvent = self.wheel_event
        f1.listWidget.dropEvent = self.drop_annotation_src_to_des
        f1.listWidget_2.dropEvent = self.drop_region_src_to_des
        # self.Form[0].listWidget_2.mousePressEvent = self.click_on_dest
        # self.Form[1].listWidget_2.mousePressEvent = self.click_on_src

        # UI 功能連結
        self.UI.action_Save.triggered.connect(self.save_file)
        self.UI.action_Delete.triggered.connect(self.delete_selected_rows)
        self.UI.actionConvert_to_simple_name.triggered.connect(self.convert_to_simple_naming)
        self.UI.actionConvert_to_VIA_naming.triggered.connect(self.convert_to_VIA_naming)
        self.Form[0].listWidget.currentRowChanged.connect(lambda: self.update_preview(0))
        self.Form[0].listWidget_2.currentRowChanged.connect(lambda: self.show_attribute(0))
        self.Form[0].tableWidget.cellChanged.connect(self.edit_attribute)
        self.Form[1].listWidget.currentRowChanged.connect(lambda: self.update_preview(1))
        self.Form[1].listWidget_2.currentRowChanged.connect(lambda: self.show_attribute(1))

    # 更新預覽
    def update_preview(self, idx: int):
        self.on_form = idx
        curr_text = self.Form[idx].listWidget.currentItem().text()
        f_name = f"{self.directory}/{self.json_in[idx][curr_text]['filename']}"
        if self.FormPreview is None:
            self.FormPreview = self.scene.addPixmap(QPixmap(f_name))
        else:
            self.FormPreview.setPixmap(QPixmap(f_name))
        self.UI.graphicsView.fitInView(self.FormPreview, Qt.KeepAspectRatio)
        self.zoom = self.UI.graphicsView.viewportTransform().m11()

        # Populate ListWidget
        self.Form[idx].listWidget_2.clear()
        # self.Form[idx].listWidget_3.clear()
        self.Form[idx].tableWidget.clear()
        for i, region in enumerate(self.json_in[idx][curr_text]['regions']):
            # print(i, region['region_attributes'])
            # self.UI.listWidget.addItem(filename)
            self.Form[idx].listWidget_2.addItem(str(i))

        for mk in self.mark:
            self.scene.removeItem(mk)
        self.mark.clear()
        for curr_idx in range(self.Form[idx].listWidget_2.count()):
            area: QPolygonF = QPolygonF()
            p = self.json_in[idx][curr_text]['regions'][curr_idx]['shape_attributes']
            for i in range(len(p['all_points_x'])):
                area.append(QPointF(p['all_points_x'][i], p['all_points_y'][i]))
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
        for i, attr in enumerate(r):
            # self.Form[idx].listWidget_3.addItem(f"{attr}: {r[attr]}")
            table.setItem(i, 0, QTableWidgetItem(attr))
            table.setItem(i, 1, QTableWidgetItem(r[attr]))
        table.show()

    def edit_attribute(self, i, j):
        print(f'cell {i, j} changes')
        f1: Ui_Form = self.Form[0]
        a = f1.listWidget.currentItem().text()
        r = self.json_in[0][a]['regions']
        idx = f1.listWidget_2.currentRow()
        attr = r[idx]['region_attributes']
        try:
            if j > 0:
                key = list(attr.keys())[i]
                attr[key] = f1.tableWidget.item(i, j).text()
            else:
                key = list(attr.keys())[i]
                del attr[key]
                val = list(attr.values())[j]
                attr[f1.tableWidget.item(i, j).text()] = val
            # f1.tableWidget.cellChanged.connect(lambda: print('do nothing'))
        except IndexError:
            return

    def key_event(self, e: QKeyEvent):
        key = e.key()
        if key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.zoom_preview(0.1)
        elif key == Qt.Key_Minus:
            self.zoom_preview(-0.1)

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

                self.json_in[0][in_text] = self.json_in[1][in_text]
                print('drop accepted')
                self.update_preview()
        else:
            print('drop denied')

    def drop_region_src_to_des(self, e: QDropEvent):
        print('dropped')
        f1: Ui_Form = self.Form[0]
        f2: Ui_Form = self.Form[1]
        src: QListWidget = e.source()
        src_text = f2.listWidget.currentItem().text()
        des_text = f1.listWidget.currentItem().text()
        self.json_in[0][des_text]['regions'].append(self.json_in[1][src_text]['regions'][src.currentRow()])
        self.update_preview(0)

    def zoom_preview(self, delta_y: float):
        m: QTransform = QTransform()
        self.zoom = max(min(self.zoom + delta_y, 10), 0.01)
        m.scale(self.zoom, self.zoom)
        # print(delta_y, self.zoom)
        self.UI.graphicsView.setTransform(m)

    # 另存異動後 JSON 檔案
    def save_file(self):
        json_out = {}
        for i in range(self.UI.listWidget.count()):
            filename = self.UI.listWidget.item(i).text()
            json_out[filename] = self.json_in[filename]

        with open('../modified_json.json', 'w') as json_file:
            json_file.write(str(json.dumps(json_out)))

    # 刪除選取項目
    def delete_selected_rows(self):
        while len(self.UI.listWidget.selectedIndexes()) > 0:
            selections = self.UI.listWidget.selectedIndexes()
            self.UI.listWidget.takeItem(selections[0].row())

    def convert_to_simple_naming(self):
        json_out = {}
        for i in range(self.UI.listWidget.count()):
            in_f_name = self.UI.listWidget.item(i).text()
            out_f_name = self.json_in[in_f_name]['filename']
            json_out[out_f_name] = self.json_in[in_f_name]

        self.json_in = json_out
        # Re-Populate ListWidget
        self.UI.listWidget.clear()
        for i, filename in enumerate(self.json_in):
            self.UI.listWidget.addItem(filename)

    def convert_to_VIA_naming(self):
        json_out = {}
        for i in range(self.UI.listWidget.count()):
            in_f_name = self.UI.listWidget.item(i).text()
            out_f_name = self.json_in[in_f_name]['filename']
            f_size = self.json_in[in_f_name]['size']
            out_f_name = f'{out_f_name}{f_size}'
            json_out[out_f_name] = self.json_in[in_f_name]

        self.json_in = json_out
        # Re-Populate ListWidget
        self.UI.listWidget.clear()
        for i, filename in enumerate(self.json_in):
            self.UI.listWidget.addItem(filename)


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