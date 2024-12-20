# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hci_platform.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1178, 800)
        self.label_debug = QtWidgets.QLabel(Form)
        self.label_debug.setGeometry(QtCore.QRect(10, 10, 60, 25))
        self.label_debug.setObjectName("label_debug")
        self.btn_ini = QtWidgets.QPushButton(Form)
        self.btn_ini.setGeometry(QtCore.QRect(200, 10, 50, 25))
        self.btn_ini.setObjectName("btn_ini")
        self.Edit_ini = QtWidgets.QTextEdit(Form)
        self.Edit_ini.setGeometry(QtCore.QRect(10, 40, 300, 400))
        self.Edit_ini.setReadOnly(True)
        self.Edit_ini.setObjectName("Edit_ini")
        self.Edit_cmd = QtWidgets.QTextEdit(Form)
        self.Edit_cmd.setGeometry(QtCore.QRect(10, 450, 300, 200))
        self.Edit_cmd.setObjectName("Edit_cmd")
        self.btn_cmd = QtWidgets.QPushButton(Form)
        self.btn_cmd.setGeometry(QtCore.QRect(10, 720, 100, 25))
        self.btn_cmd.setObjectName("btn_cmd")
        self.btn_clear = QtWidgets.QPushButton(Form)
        self.btn_clear.setGeometry(QtCore.QRect(130, 720, 50, 25))
        self.btn_clear.setObjectName("btn_clear")
        self.Edit_log = QtWidgets.QTextEdit(Form)
        self.Edit_log.setGeometry(QtCore.QRect(320, 40, 850, 611))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.Edit_log.setPalette(palette)
        self.Edit_log.setObjectName("Edit_log")
        self.label_device = QtWidgets.QLabel(Form)
        self.label_device.setGeometry(QtCore.QRect(320, 660, 60, 25))
        self.label_device.setObjectName("label_device")
        self.btn_openDevice = QtWidgets.QPushButton(Form)
        self.btn_openDevice.setGeometry(QtCore.QRect(510, 660, 75, 25))
        self.btn_openDevice.setObjectName("btn_openDevice")
        self.label_serialBaud = QtWidgets.QLabel(Form)
        self.label_serialBaud.setGeometry(QtCore.QRect(320, 690, 60, 25))
        self.label_serialBaud.setObjectName("label_serialBaud")
        self.comboBox_serialBaud = QtWidgets.QComboBox(Form)
        self.comboBox_serialBaud.setGeometry(QtCore.QRect(390, 690, 110, 25))
        self.comboBox_serialBaud.setEditable(True)
        self.comboBox_serialBaud.setObjectName("comboBox_serialBaud")
        self.comboBox_ini = QtWidgets.QComboBox(Form)
        self.comboBox_ini.setGeometry(QtCore.QRect(70, 10, 120, 26))
        self.comboBox_ini.setEditable(True)
        self.comboBox_ini.setObjectName("comboBox_ini")
        self.comboBox_device = QtWidgets.QComboBox(Form)
        self.comboBox_device.setGeometry(QtCore.QRect(390, 660, 110, 25))
        self.comboBox_device.setEditable(True)
        self.comboBox_device.setObjectName("comboBox_device")
        self.Edit_cmdData = QtWidgets.QTextEdit(Form)
        self.Edit_cmdData.setGeometry(QtCore.QRect(10, 660, 300, 50))
        self.Edit_cmdData.setObjectName("Edit_cmdData")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_debug.setText(_translate("Form", "调试功能"))
        self.btn_ini.setText(_translate("Form", "ini"))
        self.btn_cmd.setText(_translate("Form", "发送指令"))
        self.btn_clear.setText(_translate("Form", "清空"))
        self.label_device.setText(_translate("Form", "选择设备"))
        self.btn_openDevice.setText(_translate("Form", "打开设备"))
        self.label_serialBaud.setText(_translate("Form", "串口波特率"))
