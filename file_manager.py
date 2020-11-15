import os
import json
from cv2 import inRange, threshold, findContours, RETR_TREE, RETR_FLOODFILL, CHAIN_APPROX_TC89_L1, imshow
import numpy as np
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor, QPixelFormat
from savedialog import Ui_SaveDialog
from deletedialog import Ui_DeleteDialog

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
        print(thresh.shape)
        # 尋找輪廓
        contours, hierarchy = findContours(thresh, RETR_TREE, CHAIN_APPROX_TC89_L1)
        if len(contours) != 0:
            for area in contours:
                cons.append(area)
                cols.append(i)
    return cons, cols


def add_annotation(filename: str, filesize: int, contours: list, cid: list, typename: str, file: dict):

    file[filename] = {}
    root = file[filename]
    root["filename"] = filename
    root["size"] = filesize
    root["regions"] = []

    # Area 內容
    j = 0
    for area in contours:
        sattr = {"name": "polygon", "all_points_x": [], "all_points_y": []}

        for i in range(len(area)):
            sattr["all_points_x"].append(int(area[i][0][0]))
            sattr["all_points_y"].append(int(area[i][0][1]))

        root["regions"].append(
            {
                "shape_attributes": sattr,
                "region_attributes": {
                    "Name": typename,
                    "Color": colorid[cid[j]]
                }})
        j += 1


class FileManager:
    image_list = []
    via_fname = ''
    annotations = {}
    image_dir = './'
    index = -1

    def get_file_lists(self, _labeling: bool = False):
        for file in os.listdir(self.image_dir):
            if file.endswith('.JPG') or file.endswith('.jpg'):
                self.image_list.append(file)
            if file.endswith('.json') and _labeling:
                self.via_fname = f'{self.image_dir}/{file}'
                with open(self.via_fname, 'r') as json_file:
                    self.annotations = json.load(json_file)

    # 儲存 label 圖片
    def save_label_image(self, pixmap: QPixmap):
        sig = []
        save_dialog = QDialog()
        dui = Ui_SaveDialog(sig)
        dui.setupUi(save_dialog)
        dui.labelMessage.setText("Would you like to save as a label image?")
        save_dialog.setAttribute(Qt.WA_DeleteOnClose)
        save_dialog.exec()
        if sig[0] == 3:
            return 3
        if sig[0] == 1:
            path = f'{self.image_dir}/{self.image_list[self.index]}'
            path = path[: len(path) - 4] + '.png'
            image = pixmap.toImage().convertToFormat(QImage.Format_RGB32)
            image.save(path)
            # self.ui.statusbar.showMessage(f'Label image saved ({path})')
            return 1
        if sig[0] == 2:
            return 2

    def save_annotation(self, pixmap: QPixmap):
        sig = []
        save_dialog = QDialog()
        dui = Ui_SaveDialog(sig)
        dui.setupUi(save_dialog)
        dui.labelMessage.setText("Would you like to save annotations?")
        save_dialog.setAttribute(Qt.WA_DeleteOnClose)
        save_dialog.exec()
        if sig[0] == 3:
            return 3
        if sig[0] == 1:
            fname = f'{self.image_list[self.index]}'
            fsize = self.annotations[fname]['size']
            contours, colorids = get_contours(pixmap)
            add_annotation(fname, fsize, contours, colorids, 'vehicle', self.annotations)
            with open(self.via_fname, 'w') as json_file:
                json_file.write(str(json.dumps(self.annotations)))
            return 1
        if sig[0] == 2:
            return 2

    # 儲存遮罩圖片
    def save_mask(self, pixmap: QPixmap):
        sig = []
        save_dialog = QDialog()
        dui = Ui_SaveDialog(sig)
        dui.setupUi(save_dialog)
        save_dialog.setAttribute(Qt.WA_DeleteOnClose)
        save_dialog.exec()
        if sig[0] == 3:
            return 3
        if sig[0] == 1:
            path = f'{self.image_dir}/{self.image_list[self.index]}_mask.tif'
            bit = pixmap.createMaskFromColor(QColor(0, 0, 0, 0))
            bit.save(path)
            # self.ui.statusbar.showMessage(f'Mask image saved ({path})')
            return 1
        if sig[0] == 2:
            return 2

    # 刪除遮罩圖片
    def delete_mask(self):
        path = f'{self.image_dir}/{self.image_list[self.index]}_mask.tif'
        image_exist = os.path.isfile(path)
        if not image_exist:
            return 4
        sig = []
        delete_dialog = QDialog()
        dui = Ui_DeleteDialog(sig)
        dui.setupUi(delete_dialog)
        dui.labelFilename.setText(f'{self.image_list[self.index]}_mask.tif')
        delete_dialog.setAttribute(Qt.WA_DeleteOnClose)
        delete_dialog.exec()
        if sig[0] == 1:
            os.remove(path)
        # if sig[0] == 1:
        #     idx = self.index
        #     moveto = (idx + 1) if idx < (len(self.image_list) - 1) else (idx - 1)
        #     self.ui.listWidget.setCurrentRow(moveto)
        #     path = f'{self.image_dir}/{self.mask_list[idx]}'
        #     os.remove(path)
        #     self.ui.listWidget.takeItem(idx)
        #     self.image_list.pop(idx)
        #     self.mask_list.pop(idx)
        #     self.index = moveto if idx > moveto else idx
        #     self.ui.statusbar.showMessage(f'File "{path}" has been deleted')


