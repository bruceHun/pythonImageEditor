import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor
from savedialog import Ui_SaveDialog
from deletedialog import Ui_DeleteDialog


class FileManager:
    image_list = []
    mask_list = []
    image_dir = './'
    index = -1

    def get_file_lists(self):
        for file in os.listdir(self.image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(file[: len(file) - 9] + '.JPG')
                self.mask_list.append(file)

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
            path = f'{self.image_dir}/{self.mask_list[self.index]}'
            bit = pixmap.createMaskFromColor(QColor(0, 0, 0, 0))
            bit.save(path)
            # self.ui.statusbar.showMessage(f'Mask image saved ({path})')
            return 1
        if sig[0] == 2:
            return 2

    # 刪除遮罩圖片
    def delete_mask(self):
        sig = []
        delete_dialog = QDialog()
        dui = Ui_DeleteDialog(sig)
        dui.setupUi(delete_dialog)
        dui.labelFilename.setText(self.mask_list[self.index])
        delete_dialog.setAttribute(Qt.WA_DeleteOnClose)
        delete_dialog.exec()
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
