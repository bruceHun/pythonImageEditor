import json
from typing import Union
from os import path as os_path, remove as os_remove, listdir as os_listdir

from PyQt5.QtGui import QPixmap, QPen, QBitmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QGraphicsScene, QGraphicsPixmapItem, \
    QGraphicsEllipseItem, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from ccsm_mainwindow import Ui_MainWindow
from threading import Thread
from time import sleep

# 圖片資料夾名稱對照表
DIR_MAP = {'Photogroup 1': '正拍', 'Photogroup 2': '側拍', 'Photogroup 3': '還拍'}


class CCSMarkedMasksProcessor:

    def __init__(self, _win: QMainWindow, _ui: Ui_MainWindow):
        self.json_objs: dict = {}
        self.json_dims: dict = {}
        self.win: QMainWindow = _win
        self.UI: Ui_MainWindow = _ui
        self.scene: Union[QGraphicsScene, None] = None
        self.image: Union[QGraphicsPixmapItem, None] = None
        self.mask: Union[QGraphicsPixmapItem, None] = None
        self.dir: str = ''
        self.border: int = 5000
        self.mark: Union[QGraphicsEllipseItem, None] = None
        self.focus: Union[QGraphicsItem, None] = None

    def init(self):

        # 連結 UI 功能
        self.UI.listOfObjects.currentRowChanged.connect(self.change_object)
        self.UI.listOfCameras.currentRowChanged.connect(self.load)
        self.UI.actionAuto_play.triggered.connect(self.auto_play)

        self.scene = QGraphicsScene()
        self.UI.graphicsView.setScene(self.scene)

        # 開 JSON 檔
        f_name, f_type = QFileDialog.getOpenFileName(caption='Select file', filter="JSON files (*.json)")
        self.dir = os_path.dirname(f_name)
        with open(f_name, 'r') as json_file:
            json_in = json.load(json_file)
        self.json_objs = json_in['objects']
        self.json_dims = json_in['dimensions']
        keys = [key for key in self.json_objs.keys()]
        keys.sort()
        self.UI.listOfObjects.addItems(keys)
        self.UI.listOfObjects.setCurrentRow(0)
        # cams = [key for key in self.json_objs[self.UI.listOfObjects.currentItem().text()].keys()]
        # cams.sort()
        # self.UI.listOfCameras.addItems(cams)
        # self.UI.listOfCameras.setCurrentRow(0)

    def change_object(self):
        obj = self.UI.listOfObjects.currentItem().text()
        cams = [key for key in self.json_objs[obj].keys()]
        cams.sort()
        self.UI.listOfCameras.clear()
        self.UI.listOfCameras.addItems(cams)
        self.UI.listOfCameras.setCurrentRow(0)

    def auto_play(self):
        cnt = self.UI.listOfCameras.count()
        next_row = 0
        while next_row < cnt:
            next_row = next_row + 1
            print(f'load {next_row}')
            t = Thread(target=self.UI.listOfCameras.setCurrentRow(next_row))
            t.start()
            t.join()
            sleep(1)

    def load(self, idx: int = -1):
        obj = self.UI.listOfObjects.currentItem().text()
        if idx < 0:
            curr_item = self.UI.listOfCameras.currentItem()
        else:
            curr_item = self.UI.listOfCameras.item(idx)
        if curr_item is None:
            return
        cam = curr_item.text()
        dir_label, f_name = cam.split('/')
        # print(f'{self.dir}/{DIR_MAP[dir_label]}/{f_name}')
        pixmap = QPixmap(f'{self.dir}/{DIR_MAP[dir_label]}/{f_name}')

        if self.image is None:
            self.image = self.scene.addPixmap(pixmap)
        else:
            self.image.setPixmap(pixmap)

        blank = QPixmap(pixmap.size())
        m_name = f'{self.dir}/{DIR_MAP[dir_label]}/{os_path.splitext(f_name)[0]}_mask.tif'

        if os_path.exists(m_name):
            # print(m_name)
            blank.fill(Qt.magenta)
            blank.setMask(QBitmap(m_name))
        else:
            blank.fill(Qt.transparent)
        if self.mark is None:
            self.mask = self.scene.addPixmap(blank)
            self.mask.setOpacity(0.5)
        else:
            self.mask.setPixmap(blank)
        b_top = -self.border
        b_btm = 2 * self.border
        self.scene.setSceneRect(
            QRectF(b_top, b_top, pixmap.width() + b_btm, pixmap.height() + b_btm)
        )
        x, y, dist = self.json_objs[obj][cam]
        # print(x, y, dist)
        r = 30000 / dist
        r2 = r + r
        if self.mark is not None:
            self.scene.removeItem(self.mark)
            self.scene.removeItem(self.focus)
        self.mark = self.scene.addEllipse(QRectF(0, 0, r2, r2), QPen(Qt.yellow, 10))
        self.focus = self.scene.addRect(QRectF(0, 0, r2 + 200, r2 + 200))
        self.mark.setPos(x - r, y - r)
        self.focus.setPos(x - r - 100, y - r - 100)
        self.UI.graphicsView.fitInView(self.focus, Qt.KeepAspectRatio)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MMP = CCSMarkedMasksProcessor(MainWindow, ui)
    MMP.init()
    lock = 0
    MainWindow.show()
    sys.exit(app.exec_())
