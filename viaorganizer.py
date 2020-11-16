from PyQt5.QtWidgets import QFileDialog

from viaorganizer_ui import Ui_MainWindow
from PyQt5 import QtWidgets
import json


class ViaOrganizer:
    UI: Ui_MainWindow = None
    win: QtWidgets.QMainWindow
    json_in = {}

    def __init__(self, _ui: Ui_MainWindow, _win: QtWidgets.QMainWindow):
        self.UI = _ui
        self.win = _win

    def init(self):
        # 開 JSON 檔
        f_name, f_type = QFileDialog.getOpenFileName(filter="JSON files (*.json)")
        with open(f_name, 'r') as json_file:
            self.json_in = json.load(json_file)
        print(len(self.json_in))

        # Populate ListWidget
        for i, filename in enumerate(self.json_in):
            self.UI.listWidget.addItem(filename)

        # UI 功能連結
        self.UI.action_Save.triggered.connect(self.save_file)
        self.UI.action_Delete.triggered.connect(self.delete_selected_rows)

    # 另存異動後 JSON 檔案
    def save_file(self):
        json_out = {}
        for i in range(self.UI.listWidget.count()):
            filename = self.UI.listWidget.item(i).text()
            json_out[filename] = self.json_in[filename]

        with open('modified_json.json', 'w') as json_file:
            json_file.write(str(json.dumps(json_out)))

    # 刪除選取項目
    def delete_selected_rows(self):
        while len(self.UI.listWidget.selectedIndexes()) > 0:
            selections = self.UI.listWidget.selectedIndexes()
            self.UI.listWidget.takeItem(selections[0].row())


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
