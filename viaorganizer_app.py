import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt

from viaorganizer import Ui_MainWindow
from anno_info import Ui_Form
from PyQt5 import QtWidgets
from typing import Union
import json


class ViaOrganizer:

    def __init__(self, _ui: Ui_MainWindow, _win: QtWidgets.QMainWindow):
        self.UI: Ui_MainWindow = _ui
        self.Form1: Union[Ui_Form, None] = None
        self.Form2: Union[Ui_Form, None] = None
        self.Form1Preview: Union[QPixmap, None] = None
        self.Form2Preview: Union[QPixmap, None] = None
        self.win: QtWidgets.QMainWindow = _win
        self.directory: str = ''
        self.json_in = {}
        self.scene: Union[QtWidgets.QGraphicsScene, None] = None

    def init(self):
        # 指定圖片資料夾
        self.directory = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        # 開 JSON 檔
        f_name, f_type = QFileDialog.getOpenFileName(filter="JSON files (*.json)")
        with open(f_name, 'r') as json_file:
            self.json_in = json.load(json_file)
        print(len(self.json_in))
        sub = QtWidgets.QMdiSubWindow()
        form = QtWidgets.QWidget()
        self.Form1 = Ui_Form()
        self.Form1.setupUi(form)
        sub.setWidget(form)
        self.UI.mdiArea.addSubWindow(sub)
        sub.show()
        # Populate ListWidget
        for i, filename in enumerate(self.json_in):
            # self.UI.listWidget.addItem(filename)
            self.Form1.listWidget.addItem(filename)

        self.scene = QtWidgets.QGraphicsScene()
        self.UI.graphicsView.setScene(self.scene)

        self.Form1.listWidget.setCurrentRow(0)
        self.form1_change_preview()

        # UI 功能連結
        self.UI.action_Save.triggered.connect(self.save_file)
        self.UI.action_Delete.triggered.connect(self.delete_selected_rows)
        self.UI.actionConvert_to_simple_name.triggered.connect(self.convert_to_simple_naming)
        self.UI.actionConvert_to_VIA_naming.triggered.connect(self.convert_to_VIA_naming)

        self.Form1.listWidget.currentRowChanged.connect(self.form1_change_preview)
        self.Form1.listWidget_2.currentRowChanged.connect(self.form1_show_attribute)

    # 更新預覽
    def form1_change_preview(self):
        curr_idx = self.Form1.listWidget.currentRow()
        curr_text = self.Form1.listWidget.item(curr_idx).text()
        f_name = f'{self.directory}/{curr_text}'
        base_name, extension = os.path.splitext(f_name)
        extension = ''.join(c for c in extension if not c.isdigit())
        f_name = f'{base_name}{extension}'
        if self.Form1Preview is None:
            self.Form1Preview = self.scene.addPixmap(QPixmap(f_name))
        else:
            self.Form1Preview.setPixmap(QPixmap(f_name))
        self.UI.graphicsView.fitInView(self.Form1Preview, Qt.KeepAspectRatio)

        # Populate ListWidget
        for i, region in enumerate(self.json_in[curr_text]['regions']):
            print(i, region['region_attributes'])
            # self.UI.listWidget.addItem(filename)
            self.Form1.listWidget_2.addItem(str(i))

    def form1_show_attribute(self):
        curr_idx = self.Form1.listWidget_2.currentRow()
        # Populate ListWidget
        self.Form1.listWidget_3.clear()
        for i, attr in enumerate(self.json_in[self.Form1.listWidget.currentItem().text()]['regions'][curr_idx]['region_attributes']):
            # self.UI.listWidget.addItem(filename)
            self.Form1.listWidget_3.addItem(attr)

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