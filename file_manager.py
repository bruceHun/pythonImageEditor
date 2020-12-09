from os import path as os_path, remove as os_remove, listdir as os_listdir
import json
from threading import Thread

from PyQt5.QtCore import QPoint
from cv2 import inRange, threshold, findContours, RETR_TREE, CHAIN_APPROX_SIMPLE
import numpy as np
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPolygon, QPen, QBrush
from re import search as re_search, sub as re_sub

lows: np.array = np.array([[128, 0, 0, 255],
                           [0, 128, 0, 255],
                           [0, 0, 128, 255],
                           [128, 128, 0, 255],
                           [128, 0, 128, 255],
                           [0, 128, 128, 255]])

highs: np.array = np.array([[255, 0, 0, 255],
                            [0, 255, 0, 255],
                            [0, 0, 255, 255],
                            [255, 255, 0, 255],
                            [255, 0, 255, 255],
                            [0, 255, 255, 255]])

# Rearrange order to subtly convert RGB to BGR
colorid = ['Blue', 'Green', 'Red', 'Aqua', 'Fuchsia', 'Yellow']


def get_contours(pixmap: QPixmap):
    cons = []
    cols = []

    image = pixmap.toImage().convertToFormat(QImage.Format_RGB32)
    byte_str = image.bits()
    byte_str.setsize(image.byteCount())
    # Using the np.frombuffer function to convert the byte string into an np array
    img = np.frombuffer(byte_str, dtype=np.uint8).reshape((pixmap.height(), pixmap.width(), 4))

    for i in range(6):
        output = inRange(img, lows[i], highs[i])
        ret, thresh = threshold(output, 128, 255, 0)
        # thresh = np.where(img == colorlist[i], 255, 0)
        # 尋找輪廓
        contours, hierarchy = findContours(thresh, RETR_TREE, CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            for area in contours:
                cons.append(area)
                cols.append(i)
    return cons, cols


def add_regions(_regions: list, typename: str, pixmap: QPixmap):
    contours, cids = get_contours(pixmap)
    # Area 內容
    j = 0
    for area in contours:
        sattr = {"name": "polygon", "all_points_x": [], "all_points_y": []}

        for i in range(len(area)):
            sattr["all_points_x"].append(int(area[i][0][0]))
            sattr["all_points_y"].append(int(area[i][0][1]))

        _regions.append(
            {
                "shape_attributes": sattr,
                "region_attributes": {
                    "Name": typename,
                    "Color": colorid[cids[j]]
                }})
        j += 1


def add_annotation(filename: str, filesize: int, file: dict) -> list:
    a_name = f'{filename}{filesize}'
    file[a_name] = {}
    root = file[a_name]
    root["filename"] = filename
    root["size"] = filesize
    root["regions"] = []
    return root["regions"]


class FileManager:

    def __init__(self):
        self.image_list: list = []
        self.via_fname: str = ''
        self.annotations: dict = {}
        self.image_dir: str = './'
        self.index: int = -1
        self.dialog_root = None

    def set_dialog_root(self, _parent):
        self.dialog_root = _parent

    def get_file_lists(self, show_annotated_only: bool = False):
        f_index = 1
        for file in os_listdir(self.image_dir):
            f_lower = file.lower()
            if f_lower.endswith('.json'):
                self.via_fname = f'{self.image_dir}/{file}'
                with open(self.via_fname, 'r') as json_file:
                    self.annotations = json.load(json_file)
                if show_annotated_only:
                    for key, val in self.annotations.items():
                        self.image_list.append(f"[{f_index}] {val['filename']}")
                        f_index += 1
            if not show_annotated_only:
                if f_lower.endswith('.jpg') or f_lower.endswith('.png'):
                    self.image_list.append(f"[{f_index}] {file}")
                    f_index += 1

    def save_annotation(self, pixmap: dict):
        result = QMessageBox.question(self.dialog_root,
                                      "Save changes?",
                                      "Would you like to save your changes?\n"
                                      "\n[Yes] saves your changes"
                                      "\n[No]  discards your changes",
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if result == QMessageBox.Yes:
            fname = re_sub("\\[([0-9]+)\\] ", "", self.image_list[self.index])
            try:
                fsize = self.annotations[fname]['size']
            except KeyError:
                fsize = os_path.getsize(f'{self.image_dir}/{fname}')
            # fname = f'{fname}{fsize}'
            # 創建圖片資訊
            r = add_annotation(fname, fsize, self.annotations)
            # 加入區域
            threads = []
            for t_name, pix in pixmap.items():
                t = Thread(target=add_regions(r, t_name, pix))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            # 寫入 JSON 檔
            if self.via_fname == '':
                self.via_fname = f'{self.image_dir}/via_region_data.json'
            with open(self.via_fname, 'w') as json_file:
                json_file.write(str(json.dumps(self.annotations)))
            return 1

        elif result == QMessageBox.No:
            return 2

        elif result == QMessageBox.Cancel:
            return 3

    # 儲存遮罩圖片
    def save_mask(self, pixmaps: dict):
        result = QMessageBox.question(self.dialog_root,
                                      "Export to mask file?",
                                      "Would you like to export current mask to an image file?",
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            pixmap: QPixmap = QPixmap()
            painter: QPainter = QPainter()
            i = 0
            for key, val in pixmaps.items():
                if i == 0:
                    pixmap = val.copy()
                    painter = QPainter(pixmap)
                else:
                    painter.drawPixmap(0, 0, val)
                i += 1
            painter.end()
            f_name = os_path.basename(re_sub("\\[([0-9]+)\\] ", "", self.image_list[self.index]))
            path = f'{self.image_dir}/{f_name}_mask.tif'
            bit = pixmap.createMaskFromColor(QColor(0, 0, 0, 0))
            bit.save(path)
            # self.ui.statusbar.showMessage(f'Mask image saved ({path})')
            return 1
        elif result == QMessageBox.No:
            return 2

    # 刪除遮罩圖片
    def delete_mask(self):
        path = f'{self.image_dir}/{self.image_list[self.index]}_mask.tif'
        image_exist = os_path.isfile(path)
        if not image_exist:
            return 4
        result = QMessageBox.question(self.dialog_root,
                                      "Delete mask file?",
                                      "Are you sure that you want to permanently delete this file?"
                                      f'{self.image_list[self.index]}_mask.tif',
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            os_remove(path)

    def export_all(self):

        _index = 0
        for data in self.annotations.values():
            retrieved_name = re_sub("\\[([0-9]+)\\] ", "", self.image_list[_index])
            f_name = f'{self.image_dir}/{retrieved_name}'
            pix = QPixmap(f_name)
            print(f_name)

            # Making mask
            blank = QPixmap(pix.size())
            blank.fill(QColor(0, 0, 0, 0))
            del pix

            painter = QPainter(blank)
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))

            for r in data["regions"]:
                p = r['shape_attributes']
                points = [QPoint(p['all_points_x'][i], p['all_points_y'][i]) for i in range(len(p['all_points_x']))]
                painter.drawPolygon(QPolygon(points))

            painter.end()

            # Generate mask image
            mask_image = blank.createMaskFromColor(QColor(0, 0, 0, 0))
            # Save output
            file_name = self.image_dir + '/' + os_path.basename(f_name) + "_mask.tif"
            mask_image.save(file_name)
            print("Saved to ", file_name)
            _index += 1
