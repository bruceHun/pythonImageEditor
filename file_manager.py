import os
import json
from cv2 import inRange, threshold, findContours, RETR_TREE, CHAIN_APPROX_TC89_L1
import numpy as np
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter

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
        contours, hierarchy = findContours(thresh, RETR_TREE, CHAIN_APPROX_TC89_L1)
        if len(contours) != 0:
            for area in contours:
                cons.append(area)
                cols.append(i)
    return cons, cols


def add_regions(_regions: list, contours: list, cid: list, typename: str):
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
                    "Color": colorid[cid[j]]
                }})
        j += 1


def add_annotation(filename: str, filesize: int, file: dict) -> list:
    file[filename] = {}
    root = file[filename]
    root["filename"] = filename
    root["size"] = filesize
    root["regions"] = []
    return root["regions"]


class FileManager:
    image_list = []
    via_fname = ''
    annotations = {}
    image_dir = './'
    index = -1
    dialog_root: QDialog = None

    def get_file_lists(self, _labeling: bool = False):
        for file in os.listdir(self.image_dir):
            if file.endswith('.JPG') or file.endswith('.jpg') or file.endswith('.png'):
                self.image_list.append(file)
            if file.endswith('.json') and _labeling:
                self.via_fname = f'{self.image_dir}/{file}'
                with open(self.via_fname, 'r') as json_file:
                    self.annotations = json.load(json_file)

    def save_annotation(self, pixmap: dict):
        if self.dialog_root is None:
            self.dialog_root = QDialog()
        result = QMessageBox.question(self.dialog_root,
                                      "Save changes?",
                                      "Would you like to save your changes?\n"
                                      "\n[Yes] Save changes"
                                      "\n[No] Discard changes",
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if result == QMessageBox.Yes:
            fname = f'{self.image_list[self.index]}'
            try:
                fsize = self.annotations[fname]['size']
            except KeyError:
                fsize = os.path.getsize(f'{self.image_dir}/{self.image_list[self.index]}')
            fname = f'{fname}{fsize}'
            # 創建圖片資訊
            r = add_annotation(fname, fsize, self.annotations)
            # 加入區域
            for t_name, pix in pixmap.items():
                contours, colorids = get_contours(pix)
                add_regions(r, contours, colorids, t_name)
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
        if self.dialog_root is None:
            self.dialog_root = QDialog()
        result = QMessageBox.question(self.dialog_root,
                                      "Export to mask file?",
                                      "Would you like to export current image?",
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
                    painter.drawPixmap(val)
                i += 1
            painter.end()

            path = f'{self.image_dir}/{self.image_list[self.index]}_mask.tif'
            bit = pixmap.createMaskFromColor(QColor(0, 0, 0, 0))
            bit.save(path)
            # self.ui.statusbar.showMessage(f'Mask image saved ({path})')
            return 1
        elif result == QMessageBox.No:
            return 2

    # 刪除遮罩圖片
    def delete_mask(self):
        path = f'{self.image_dir}/{self.image_list[self.index]}_mask.tif'
        image_exist = os.path.isfile(path)
        if not image_exist:
            return 4
        if self.dialog_root is None:
            self.dialog_root = QDialog()
        result = QMessageBox.question(self.dialog_root,
                                      "Delete mask file?",
                                      "Would you like to delete the following file?"
                                      f'{self.image_list[self.index]}_mask.tif',
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            os.remove(path)

