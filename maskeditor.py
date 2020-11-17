from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets
from image_processor import ImageProcessor


class MaskEditor:
    ui: Ui_MainWindow = None
    win: QtWidgets.QMainWindow = None
    IP: ImageProcessor = ImageProcessor()

    def __init__(self, _ui: Ui_MainWindow, _win: QtWidgets.QMainWindow):
        self.ui = _ui
        self.win = _win
        self.IP.ui = _ui
        self.IP.init()
        self.IP.main_window = _win

        # 滑鼠事件
        self.ui.graphicsView.mouseMoveEvent = self.IP.mouse_movement
        self.ui.graphicsView.mousePressEvent = self.IP.start_paint
        self.ui.graphicsView.mouseReleaseEvent = self.IP.end_paint
        # 鍵盤事件
        self.win.keyPressEvent = self.IP.key_event
        # 滾輪事件
        self.ui.graphicsView.wheelEvent = self.IP.mouse_wheel_event
        # 離開程式事件
        self.win.closeEvent = self.IP.on_exit
        # 調整視窗大小事件
        self.win.resizeEvent = self.IP.scale_to_fit

    def init(self):
        # 產生繪圖場景
        self.IP.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(self.IP.scene)
        # 連結 UI 功能
        self.ui.action_Open.triggered.connect(lambda: self.IP.init(True))
        self.ui.action_Save_Mask.triggered.connect(self.IP.save_mask)
        self.ui.actionSave_Label.triggered.connect(lambda: self.IP.change_image(self.IP.FM.index))
        self.ui.action_Quit.triggered.connect(self.win.close)
        self.ui.action_Undo.triggered.connect(self.IP.undo_changes)
        self.ui.action_Redo.triggered.connect(self.IP.redo_changes)
        self.ui.actionDelete.triggered.connect(self.IP.delete_mask)
        self.ui.FuncBtn1.clicked.connect(lambda: self.IP.change_image(max(self.IP.FM.index - 1, 0)))
        self.ui.FuncBtn2.clicked.connect(
            lambda: self.IP.change_image(min(self.IP.FM.index + 1, len(self.IP.FM.image_list) - 1)))
        self.ui.FuncBtn5.clicked.connect(lambda: self.IP.scale_display(self.IP.zoom_scale))
        self.ui.FuncBtn6.clicked.connect(lambda: self.IP.scale_display(-self.IP.zoom_scale))
        self.ui.listWidget.itemClicked.connect(lambda: self.IP.change_image(self.ui.listWidget.currentRow()))
        self.ui.BrushSizeSlider.valueChanged.connect(self.IP.change_brush_size)
        self.ui.brightnessSlider.valueChanged.connect(self.IP.change_photo_brightness)
        self.ui.ColorBtn1.clicked.connect(lambda: self.IP.change_brush_color(0))
        self.ui.ColorBtn2.clicked.connect(lambda: self.IP.change_brush_color(1))
        self.ui.ColorBtn3.clicked.connect(lambda: self.IP.change_brush_color(2))
        self.ui.ColorBtn4.clicked.connect(lambda: self.IP.change_brush_color(3))
        self.ui.ColorBtn5.clicked.connect(lambda: self.IP.change_brush_color(4))
        self.ui.ColorBtn6.clicked.connect(lambda: self.IP.change_brush_color(5))
        self.ui.EraserBtn.clicked.connect(self.IP.erase_mode_on)

        # 檔案列表
        self.ui.listWidget.addItems(self.IP.FM.image_list)
        # 設定初始圖片
        self.IP.change_image(self.IP.FM.index)
        # 產生筆刷游標
        self.ui.BrushSizeSlider.setValue(self.IP.brush_size)
        ##


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    mapp = MaskEditor(ui, MainWindow)
    MainWindow.show()
    mapp.init()
    sys.exit(app.exec_())
