from PyQt5.QtWidgets import QMessageBox

from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from image_processor import ImageProcessor


class MaskEditor:
    UI: Ui_MainWindow = None
    win: QtWidgets.QMainWindow = None
    IP: ImageProcessor = None
    # 版本
    ver = 10

    def __init__(self, _ui: Ui_MainWindow, _win: QtWidgets.QMainWindow):
        self.UI = _ui
        self.win = _win
        self.IP = ImageProcessor()
        self.IP.UI = _ui
        self.IP.init()
        self.IP.main_window = _win

        # 滑鼠事件
        self.UI.graphicsView.mouseMoveEvent = self.IP.mouse_movement
        self.UI.graphicsView.mousePressEvent = self.IP.start_paint
        self.UI.graphicsView.mouseReleaseEvent = self.IP.end_paint
        # 鍵盤事件
        self.win.keyPressEvent = self.IP.key_event
        # 滾輪事件
        self.UI.graphicsView.wheelEvent = self.IP.mouse_wheel_event
        # 離開程式事件
        self.win.closeEvent = self.IP.on_exit
        # 調整視窗大小事件
        self.win.resizeEvent = self.IP.scale_to_fit

    def init(self):
        # 產生繪圖場景
        self.IP.scene = QtWidgets.QGraphicsScene()
        self.UI.graphicsView.setScene(self.IP.scene)
        # 連結 UI 功能
        # 功能表
        self.UI.action_Open.triggered.connect(lambda: self.IP.init(True))
        self.UI.action_Export_to_Mask.triggered.connect(self.IP.save_mask)
        self.UI.action_Save.triggered.connect(self.IP.refresh_masks)
        self.UI.action_Settings.triggered.connect(self.IP.change_settings)
        self.UI.action_Quit.triggered.connect(self.win.close)
        self.UI.action_Undo.triggered.connect(self.IP.undo_changes)
        self.UI.action_Redo.triggered.connect(self.IP.redo_changes)
        self.UI.action_Delete.triggered.connect(self.IP.delete_mask)
        self.UI.action_Add_Class.triggered.connect(self.IP.add_class)
        self.UI.action_Select_Polygon.triggered.connect(self.IP.change_paint_mode)
        self.UI.action_Show_annotated.triggered.connect(lambda: self.IP.init(is_running=True, show_annotated_switch=True))
        # 功能按鈕
        self.UI.FuncBtn1.clicked.connect(lambda: self.IP.change_image(max(self.IP.FM.index - 1, 0)))
        self.UI.FuncBtn2.clicked.connect(
            lambda: self.IP.change_image(min(self.IP.FM.index + 1, len(self.IP.FM.image_list) - 1)))
        self.UI.FuncBtn5.clicked.connect(lambda: self.IP.scale_display(self.IP.zoom_scale))
        self.UI.FuncBtn6.clicked.connect(lambda: self.IP.scale_display(-self.IP.zoom_scale))
        # 檔案清單
        self.UI.listWidget.itemClicked.connect(lambda: self.IP.change_image(self.UI.listWidget.currentRow()))
        # 滑條
        self.UI.BrushSizeSlider.valueChanged.connect(self.IP.change_brush_size)
        self.UI.brightnessSlider.valueChanged.connect(self.IP.change_photo_brightness)
        # 顏色按鈕
        self.UI.ColorBtn1.clicked.connect(lambda: self.IP.change_brush_color(0))
        self.UI.ColorBtn2.clicked.connect(lambda: self.IP.change_brush_color(1))
        self.UI.ColorBtn3.clicked.connect(lambda: self.IP.change_brush_color(2))
        self.UI.ColorBtn4.clicked.connect(lambda: self.IP.change_brush_color(3))
        self.UI.ColorBtn5.clicked.connect(lambda: self.IP.change_brush_color(4))
        self.UI.ColorBtn6.clicked.connect(lambda: self.IP.change_brush_color(5))
        self.UI.EraserBtn.clicked.connect(self.IP.erase_mode_on)

        # 檔案列表
        self.UI.listWidget.addItems(self.IP.FM.image_list)
        # 設定初始圖片
        self.IP.change_image(self.IP.FM.index)
        # 產生筆刷游標
        self.UI.BrushSizeSlider.setValue(self.IP.brush_size)
        self.IP.gen_brush()
        ##


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    UI = Ui_MainWindow()
    UI.setupUi(MainWindow)
    mapp = MaskEditor(UI, MainWindow)
    MainWindow.show()
    mapp.init()
    sys.exit(app.exec_())
