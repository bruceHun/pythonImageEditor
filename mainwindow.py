# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(961, 533)
        MainWindow.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.SideBar = QtWidgets.QVBoxLayout()
        self.SideBar.setObjectName("SideBar")
        self.NumOfImageslabel = QtWidgets.QLabel(self.centralwidget)
        self.NumOfImageslabel.setFocusPolicy(QtCore.Qt.NoFocus)
        self.NumOfImageslabel.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.NumOfImageslabel.setObjectName("NumOfImageslabel")
        self.SideBar.addWidget(self.NumOfImageslabel)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QtCore.QSize(200, 0))
        self.listWidget.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.listWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.listWidget.setAutoFillBackground(False)
        self.listWidget.setStyleSheet("background-color: rgb(200, 200, 200);")
        self.listWidget.setAlternatingRowColors(False)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listWidget.setSelectionRectVisible(False)
        self.listWidget.setObjectName("listWidget")
        self.SideBar.addWidget(self.listWidget)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.labelBrushSize = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelBrushSize.sizePolicy().hasHeightForWidth())
        self.labelBrushSize.setSizePolicy(sizePolicy)
        self.labelBrushSize.setMinimumSize(QtCore.QSize(80, 0))
        self.labelBrushSize.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.labelBrushSize.setObjectName("labelBrushSize")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelBrushSize)
        self.BrushSizeSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BrushSizeSlider.sizePolicy().hasHeightForWidth())
        self.BrushSizeSlider.setSizePolicy(sizePolicy)
        self.BrushSizeSlider.setMinimumSize(QtCore.QSize(0, 0))
        self.BrushSizeSlider.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.BrushSizeSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.BrushSizeSlider.setMinimum(5)
        self.BrushSizeSlider.setMaximum(600)
        self.BrushSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.BrushSizeSlider.setObjectName("BrushSizeSlider")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.BrushSizeSlider)
        self.labelCurrClass = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurrClass.sizePolicy().hasHeightForWidth())
        self.labelCurrClass.setSizePolicy(sizePolicy)
        self.labelCurrClass.setMinimumSize(QtCore.QSize(80, 0))
        self.labelCurrClass.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.labelCurrClass.setObjectName("labelCurrClass")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelCurrClass)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.comboBox.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.comboBox.setObjectName("comboBox")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.Brightnesslabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Brightnesslabel.sizePolicy().hasHeightForWidth())
        self.Brightnesslabel.setSizePolicy(sizePolicy)
        self.Brightnesslabel.setMinimumSize(QtCore.QSize(80, 0))
        self.Brightnesslabel.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.Brightnesslabel.setObjectName("Brightnesslabel")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.Brightnesslabel)
        self.brightnessSlider = QtWidgets.QSlider(self.centralwidget)
        self.brightnessSlider.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.brightnessSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.brightnessSlider.setMaximum(100)
        self.brightnessSlider.setSingleStep(10)
        self.brightnessSlider.setProperty("value", 100)
        self.brightnessSlider.setOrientation(QtCore.Qt.Horizontal)
        self.brightnessSlider.setObjectName("brightnessSlider")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.brightnessSlider)
        self.HideLayerCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.HideLayerCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.HideLayerCheckBox.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.HideLayerCheckBox.setObjectName("HideLayerCheckBox")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.HideLayerCheckBox)
        self.SideBar.addLayout(self.formLayout_2)
        self.ImageBrightnessPanel = QtWidgets.QHBoxLayout()
        self.ImageBrightnessPanel.setObjectName("ImageBrightnessPanel")
        self.SideBar.addLayout(self.ImageBrightnessPanel)
        self.BrushColorPanel = QtWidgets.QGridLayout()
        self.BrushColorPanel.setObjectName("BrushColorPanel")
        self.ColorBtn2 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn2.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.ColorBtn2.setText("")
        self.ColorBtn2.setObjectName("ColorBtn2")
        self.BrushColorPanel.addWidget(self.ColorBtn2, 0, 2, 1, 1)
        self.ColorBtn1 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn1.setStyleSheet("background-color: rgb(252, 0, 0);\n"
"selection-background-color: rgb(0, 0, 255);")
        self.ColorBtn1.setText("")
        self.ColorBtn1.setObjectName("ColorBtn1")
        self.BrushColorPanel.addWidget(self.ColorBtn1, 0, 1, 1, 1)
        self.labelBrushColor = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelBrushColor.sizePolicy().hasHeightForWidth())
        self.labelBrushColor.setSizePolicy(sizePolicy)
        self.labelBrushColor.setMinimumSize(QtCore.QSize(80, 0))
        self.labelBrushColor.setMaximumSize(QtCore.QSize(80, 16777215))
        self.labelBrushColor.setFocusPolicy(QtCore.Qt.NoFocus)
        self.labelBrushColor.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.labelBrushColor.setObjectName("labelBrushColor")
        self.BrushColorPanel.addWidget(self.labelBrushColor, 0, 0, 1, 1)
        self.ColorBtn3 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn3.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn3.setStyleSheet("background-color: rgb(0, 0, 255);")
        self.ColorBtn3.setText("")
        self.ColorBtn3.setObjectName("ColorBtn3")
        self.BrushColorPanel.addWidget(self.ColorBtn3, 0, 3, 1, 1)
        self.ColorBtn6 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn6.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn6.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn6.setStyleSheet("background-color: rgb(0, 255, 255);")
        self.ColorBtn6.setText("")
        self.ColorBtn6.setObjectName("ColorBtn6")
        self.BrushColorPanel.addWidget(self.ColorBtn6, 1, 3, 1, 1)
        self.ColorBtn5 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn5.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn5.setStyleSheet("background-color: rgb(255, 0, 255);")
        self.ColorBtn5.setText("")
        self.ColorBtn5.setObjectName("ColorBtn5")
        self.BrushColorPanel.addWidget(self.ColorBtn5, 1, 2, 1, 1)
        self.ColorBtn4 = QtWidgets.QPushButton(self.centralwidget)
        self.ColorBtn4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ColorBtn4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ColorBtn4.setStyleSheet("background-color: rgb(255, 255, 0);")
        self.ColorBtn4.setText("")
        self.ColorBtn4.setObjectName("ColorBtn4")
        self.BrushColorPanel.addWidget(self.ColorBtn4, 1, 1, 1, 1)
        self.SideBar.addLayout(self.BrushColorPanel)
        self.EraserBtn = QtWidgets.QPushButton(self.centralwidget)
        self.EraserBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.EraserBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.EraserBtn.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";")
        self.EraserBtn.setObjectName("EraserBtn")
        self.SideBar.addWidget(self.EraserBtn)
        self.gridLayout.addLayout(self.SideBar, 0, 1, 2, 1)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setSizeIncrement(QtCore.QSize(0, 0))
        self.graphicsView.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.graphicsView.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.graphicsView.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.MainScreen = QtWidgets.QHBoxLayout()
        self.MainScreen.setObjectName("MainScreen")
        self.FuncBtn1 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn1.sizePolicy().hasHeightForWidth())
        self.FuncBtn1.setSizePolicy(sizePolicy)
        self.FuncBtn1.setMinimumSize(QtCore.QSize(50, 0))
        self.FuncBtn1.setMaximumSize(QtCore.QSize(100, 16777215))
        self.FuncBtn1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.FuncBtn1.setMouseTracking(False)
        self.FuncBtn1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.FuncBtn1.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";\n"
"selection-color: rgb(255, 170, 0);\n"
"background-color: rgb(90, 90, 90);")
        self.FuncBtn1.setObjectName("FuncBtn1")
        self.MainScreen.addWidget(self.FuncBtn1)
        self.FuncBtn2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn2.sizePolicy().hasHeightForWidth())
        self.FuncBtn2.setSizePolicy(sizePolicy)
        self.FuncBtn2.setMinimumSize(QtCore.QSize(50, 0))
        self.FuncBtn2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.FuncBtn2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.FuncBtn2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.FuncBtn2.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";\n"
"selection-color: rgb(255, 170, 0);\n"
"background-color: rgb(90, 90, 90);")
        self.FuncBtn2.setObjectName("FuncBtn2")
        self.MainScreen.addWidget(self.FuncBtn2)
        self.FuncBtn5 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn5.sizePolicy().hasHeightForWidth())
        self.FuncBtn5.setSizePolicy(sizePolicy)
        self.FuncBtn5.setMinimumSize(QtCore.QSize(50, 0))
        self.FuncBtn5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.FuncBtn5.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.FuncBtn5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.FuncBtn5.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";\n"
"selection-color: rgb(255, 170, 0);\n"
"background-color: rgb(90, 90, 90);")
        self.FuncBtn5.setObjectName("FuncBtn5")
        self.MainScreen.addWidget(self.FuncBtn5)
        self.FuncBtn6 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FuncBtn6.sizePolicy().hasHeightForWidth())
        self.FuncBtn6.setSizePolicy(sizePolicy)
        self.FuncBtn6.setMinimumSize(QtCore.QSize(50, 0))
        self.FuncBtn6.setMaximumSize(QtCore.QSize(100, 16777215))
        self.FuncBtn6.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.FuncBtn6.setFocusPolicy(QtCore.Qt.NoFocus)
        self.FuncBtn6.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 9pt \"Arial\";\n"
"selection-color: rgb(255, 170, 0);\n"
"background-color: rgb(90, 90, 90);")
        self.FuncBtn6.setObjectName("FuncBtn6")
        self.MainScreen.addWidget(self.FuncBtn6)
        self.gridLayout.addLayout(self.MainScreen, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 961, 21))
        self.menubar.setStyleSheet("color: rgb(255, 255, 255);\n"
"selection-color: rgb(255, 170, 0);")
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setStyleSheet("color: rgb(255, 255, 255);")
        self.menu_File.setObjectName("menu_File")
        self.menu_Edit = QtWidgets.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")
        self.menu_Help = QtWidgets.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_View_2 = QtWidgets.QMenu(self.menubar)
        self.menu_View_2.setObjectName("menu_View_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setStyleSheet("color: rgb(254, 204, 9);")
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Open = QtWidgets.QAction(MainWindow)
        self.action_Open.setObjectName("action_Open")
        self.action_Settings = QtWidgets.QAction(MainWindow)
        self.action_Settings.setObjectName("action_Settings")
        self.action_Undo = QtWidgets.QAction(MainWindow)
        self.action_Undo.setObjectName("action_Undo")
        self.action_Redo = QtWidgets.QAction(MainWindow)
        self.action_Redo.setObjectName("action_Redo")
        self.actionI_m_working_on_it = QtWidgets.QAction(MainWindow)
        self.actionI_m_working_on_it.setObjectName("actionI_m_working_on_it")
        self.action_Quit = QtWidgets.QAction(MainWindow)
        self.action_Quit.setObjectName("action_Quit")
        self.action_Save = QtWidgets.QAction(MainWindow)
        self.action_Save.setObjectName("action_Save")
        self.action_Delete = QtWidgets.QAction(MainWindow)
        self.action_Delete.setObjectName("action_Delete")
        self.action_Add_Class = QtWidgets.QAction(MainWindow)
        self.action_Add_Class.setObjectName("action_Add_Class")
        self.action_Export_to_Mask = QtWidgets.QAction(MainWindow)
        self.action_Export_to_Mask.setObjectName("action_Export_to_Mask")
        self.action_Select_Polygon = QtWidgets.QAction(MainWindow)
        self.action_Select_Polygon.setCheckable(True)
        self.action_Select_Polygon.setObjectName("action_Select_Polygon")
        self.action_Show_annotated = QtWidgets.QAction(MainWindow)
        self.action_Show_annotated.setCheckable(True)
        self.action_Show_annotated.setObjectName("action_Show_annotated")
        self.actionExport_All = QtWidgets.QAction(MainWindow)
        self.actionExport_All.setObjectName("actionExport_All")
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Settings)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Export_to_Mask)
        self.menu_File.addAction(self.actionExport_All)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Edit.addAction(self.action_Undo)
        self.menu_Edit.addAction(self.action_Redo)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Delete)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Add_Class)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Select_Polygon)
        self.menu_Help.addAction(self.actionI_m_working_on_it)
        self.menu_View_2.addAction(self.action_Show_annotated)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_View_2.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mask Editor"))
        self.NumOfImageslabel.setText(_translate("MainWindow", "TextLabel"))
        self.labelBrushSize.setText(_translate("MainWindow", "Brush Size"))
        self.labelCurrClass.setText(_translate("MainWindow", "Working Class"))
        self.Brightnesslabel.setText(_translate("MainWindow", "Brightness"))
        self.HideLayerCheckBox.setText(_translate("MainWindow", "Hide layer"))
        self.labelBrushColor.setText(_translate("MainWindow", "Brush Color"))
        self.EraserBtn.setText(_translate("MainWindow", "Eraser"))
        self.FuncBtn1.setText(_translate("MainWindow", "PREV"))
        self.FuncBtn2.setText(_translate("MainWindow", "NEXT"))
        self.FuncBtn5.setText(_translate("MainWindow", "+"))
        self.FuncBtn6.setText(_translate("MainWindow", "-"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Edit.setTitle(_translate("MainWindow", "Edit"))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help"))
        self.menu_View_2.setTitle(_translate("MainWindow", "&View"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
        self.action_Open.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.action_Settings.setText(_translate("MainWindow", "Settings"))
        self.action_Undo.setText(_translate("MainWindow", "&Undo"))
        self.action_Undo.setShortcut(_translate("MainWindow", "Ctrl+Z"))
        self.action_Redo.setText(_translate("MainWindow", "&Redo"))
        self.action_Redo.setShortcut(_translate("MainWindow", "Ctrl+Shift+Z"))
        self.actionI_m_working_on_it.setText(_translate("MainWindow", "I\'m working on it!"))
        self.action_Quit.setText(_translate("MainWindow", "&Quit"))
        self.action_Save.setText(_translate("MainWindow", "&Save"))
        self.action_Save.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_Delete.setText(_translate("MainWindow", "&Delete"))
        self.action_Delete.setShortcut(_translate("MainWindow", "Del"))
        self.action_Add_Class.setText(_translate("MainWindow", "&Add Class"))
        self.action_Add_Class.setShortcut(_translate("MainWindow", "C"))
        self.action_Export_to_Mask.setText(_translate("MainWindow", "&Export to Mask"))
        self.action_Select_Polygon.setText(_translate("MainWindow", "&Select Polygon"))
        self.action_Select_Polygon.setShortcut(_translate("MainWindow", "S"))
        self.action_Show_annotated.setText(_translate("MainWindow", "Show &annotated"))
        self.actionExport_All.setText(_translate("MainWindow", "Export All"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
