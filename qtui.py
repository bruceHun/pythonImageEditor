# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_img.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1071, 786)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Photo = QtWidgets.QLabel(self.centralwidget)
        self.Photo.setGeometry(QtCore.QRect(7, 4, 960, 640))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Photo.sizePolicy().hasHeightForWidth())
        self.Photo.setSizePolicy(sizePolicy)
        self.Photo.setMouseTracking(False)
        self.Photo.setScaledContents(True)
        self.Photo.setObjectName("Photo")
        self.Prev = QtWidgets.QPushButton(self.centralwidget)
        self.Prev.setGeometry(QtCore.QRect(100, 680, 93, 28))
        self.Prev.setObjectName("Prev")
        self.Next = QtWidgets.QPushButton(self.centralwidget)
        self.Next.setGeometry(QtCore.QRect(830, 680, 93, 28))
        self.Next.setObjectName("Next")
        self.MaskImage = QtWidgets.QLabel(self.centralwidget)
        self.MaskImage.setGeometry(QtCore.QRect(7, 4, 960, 640))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MaskImage.sizePolicy().hasHeightForWidth())
        self.MaskImage.setSizePolicy(sizePolicy)
        self.MaskImage.setMouseTracking(True)
        self.MaskImage.setScaledContents(True)
        self.MaskImage.setObjectName("MaskImage")
        self.brush_cursor = QtWidgets.QLabel(self.centralwidget)
        self.brush_cursor.setGeometry(QtCore.QRect(360, 210, 58, 15))
        self.brush_cursor.setText("")
        self.brush_cursor.setPixmap(QtGui.QPixmap("../../../../../Windows/System32/@EnrollmentToastIcon.png"))
        self.brush_cursor.setObjectName("brush_cursor")
        self.brush_cursor.raise_()
        self.Photo.raise_()
        self.Prev.raise_()
        self.Next.raise_()
        self.MaskImage.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1071, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Photo.setText(_translate("MainWindow", "Photo"))
        self.Prev.setText(_translate("MainWindow", "<<"))
        self.Next.setText(_translate("MainWindow", ">>"))
        self.MaskImage.setText(_translate("MainWindow", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())