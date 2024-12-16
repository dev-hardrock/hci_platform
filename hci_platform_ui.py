import os
import subprocess
import sys
import re
import serial.tools.list_ports
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QFile, QIODevice
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtGui import QCursor, QIcon, QColor, QTextFormat
from hci_platform import Ui_Form
import json
import serial


# 继承两个父类
def find_files(directory='', extersion=''):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn if
            f.endswith(extersion)]


def find_serial_port():
    port_lists = []
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        # port_lists.append(port + " " + re.sub(r'\(.*?\)', '', desc))
        port_lists.append(port)
    return port_lists


class Hci_PlatForm_Ui(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Hci_PlatForm", "Hci_PlatForm"))
        self.setWindowIcon(QIcon("./bt.svg"))

        # 获取当前程序执行路径
        self.program_path = os.path.realpath(os.path.dirname(sys.argv[0]))

        # 初始化
        self.isMousePressed = False
        self.com = QSerialPort()

        # 开启鼠标跟踪
        self.Edit_ini.viewport().setCursor(QCursor(Qt.ArrowCursor))

        # 添加创建comboBox_ini元素
        ini_files = find_files(self.program_path, ".json")
        for file in ini_files:
            self.comboBox_ini.addItem(os.path.basename(file))
        item = self.comboBox_ini.currentText()
        if not item == "":
            with open(item, 'r', encoding='utf-8') as file:
                data = json.load(file)
            for command in data['commands']:
                self.Edit_ini.append(command['command'])

        # 添加串口波特率
        self.comboBox_serialBaud.addItem("115200")
        self.comboBox_serialBaud.addItem("921600")

        # 定义一个定时器，1s定时检测串口列表
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_serial_ports)
        self.connect_signals_slots()
        self.timer.start(1000)

    def reset(self):
        self.com.close()
        self.com.setPortName("")

    def connect_signals_slots(self):
        """连接信号与槽函数"""
        # 创建btn_ini单击事件处理信号
        self.btn_ini.clicked.connect(self.open_ini)
        # 创建combobox_ini信号
        self.comboBox_ini.currentIndexChanged.connect(self.handle_ini_index_changed)
        # 创建comboBox_device处理信号
        self.comboBox_device.activated.connect(self.refresh_serial_ports)
        # 创建btn_openDevice单击事件处理信号
        self.btn_openDevice.clicked.connect(self.openDevice)
        # 创建发生指令单击事件处理信号
        self.btn_cmd.clicked.connect(self.send_hci_command)
        # 创建清空指令单击事件处理信号
        self.btn_clear.clicked.connect(self.clear_hci_command)
        # 创建创建EditIni鼠标移动信号
        self.Edit_ini.mouseMoveEvent = self.cmdMouseMoveEvent
        # 创建创建EditIni鼠标按下信号
        self.Edit_ini.mousePressEvent = self.cmdMousePressEvent
        # 创建EditIni鼠标松开信号
        self.Edit_ini.mouseReleaseEvent = self.cmdMouseReleaseEvent
        # 创建EditIni鼠标双击信号
        self.Edit_ini.mouseDoubleClickEvent = self.cmdmouseDoubleClickEvent
        # 创建Edit_cmd内容改变信号
        self.Edit_cmd.textChanged.connect(self.cmdHexDataShow)

    def cmdHexDataShow(self):
        self.Edit_cmdData.setText("changed")

    def cmdmouseDoubleClickEvent(self, event):
        return

    def cmdMouseReleaseEvent(self, event):
        self.isMousePressed = False
        cursor = self.Edit_ini.cursorForPosition(event.pos())
        # 获取光标所在行数
        line = cursor.block().blockNumber()
        print(line)
        # 检查点击是否在最后一行之后的空白区域
        text_height = 0
        for i in range(self.Edit_ini.document().blockCount()):
            block_geometry = self.Edit_ini.document().documentLayout().blockBoundingRect(self.Edit_ini.document().findBlockByNumber(i))
            text_height += block_geometry.height()
        if event.pos().y() <= text_height:
            if line >= 0:
                cmd = cursor.block().text()
                json_file = self.comboBox_ini.currentText()
                if not json_file == "":
                    with open(json_file, 'r', encoding='utf-8') as file:
                        hci_info = json.load(file)
                    for command in hci_info['commands']:
                        if command['command'] == cmd:
                            print(len(command['parameters']))
                            self.Edit_cmd.clear()
                            if len(command['parameters']) != 0:
                                self.Edit_cmd.append("{")
                                for arg in command['parameters']:
                                    self.Edit_cmd.append('  "' + arg['name'] + '": 0')
                                self.Edit_cmd.append("}")



    def cmdMousePressEvent(self, event):
        extra_selections = []
        selection = self.Edit_ini.ExtraSelection()
        # 获取光标
        selection.cursor = self.Edit_ini.cursorForPosition(event.pos())
        # 获取光标所在行数
        line = selection.cursor.block().blockNumber()
        print(line)
        # 检查点击是否在最后一行之后的空白区域
        text_height = 0
        for i in range(self.Edit_ini.document().blockCount()):
            block_geometry = self.Edit_ini.document().documentLayout().blockBoundingRect(self.Edit_ini.document().findBlockByNumber(i))
            text_height += block_geometry.height()
        if event.pos().y() <= text_height:
            if line >= 0:
                line_color = QColor(0, 120, 215)
                selection.format.setBackground(line_color)
                selection.format.setForeground(QColor("white"))
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor.clearSelection()
                extra_selections.append(selection)
                self.Edit_ini.setExtraSelections(extra_selections)
        self.isMousePressed = True

    def cmdMouseMoveEvent(self, event):
        if self.isMousePressed:
            extra_selections = []
            selection = self.Edit_ini.ExtraSelection()
            # 获取当前文本光标位置
            selection.cursor = self.Edit_ini.cursorForPosition(event.pos())
            # 文本光标移动到当前行的起始位置
            line = selection.cursor.block().blockNumber()
            print(line)
            # 检查点击是否在最后一行之后的空白区域
            text_height = 0
            for i in range(self.Edit_ini.document().blockCount()):
                block_geometry = self.Edit_ini.document().documentLayout().blockBoundingRect(
                    self.Edit_ini.document().findBlockByNumber(i))
                text_height += block_geometry.height()
            if event.pos().y() <= text_height:
                if line >= 0:
                    line_color = QColor(0, 120, 215)
                    selection.format.setBackground(line_color)
                    selection.format.setForeground(QColor("white"))
                    selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                    selection.cursor.clearSelection()
                    extra_selections.append(selection)
                    self.Edit_ini.setExtraSelections(extra_selections)

    def clear_hci_command(self):
        self.Edit_cmd.clear()

    def send_hci_command(self):
        tx_data = self.Edit_cmd.toPlainText()
        self.Edit_log.append(tx_data)
        self.Edit_log.ensureCursorVisible()
        if self.com.isOpen():
            self.com.write(tx_data)
            self.com.flush(QSerialPort.Output)

    def openDevice(self):
        text = self.btn_openDevice.text()
        portName = self.comboBox_device.currentText()
        portBaud = int(self.comboBox_serialBaud.currentText())
        if text == "打开设备":
            self.btn_openDevice.setText("关闭设备")
            self.comboBox_device.setEnabled(False)
            if not portName == "":
                self.com.setPortName(portName)
                self.com.setBaudRate(portBaud)
                self.com.setDataBits(QSerialPort.Data8)
                self.com.setParity(QSerialPort.NoParity)
                self.com.setStopBits(QSerialPort.OneStop)
                self.com.setFlowControl(QSerialPort.NoFlowControl)
                try:
                    if not self.com.open(QSerialPort.ReadWrite):
                        QMessageBox.critical(self, '错误', "设备打开失败!")
                        return
                except:
                    QMessageBox.critical(self, '错误', "设备打开失败!")
                    return

            else:
                QMessageBox.information(None, "警告", "请插入设备!")
        else:
            if not portName == "":
                self.com.close()
            self.btn_openDevice.setText("打开设备")
            self.comboBox_device.setEnabled(True)

    def refresh_serial_ports(self):
        """刷新可用串口号列表并填充到ComboBox中"""
        current_ports = QSerialPortInfo.availablePorts()
        if self.comboBox_device.currentText() == "":
            # 添加comboBox_ini
            for port in current_ports:
                port_name = port.portName()
                self.comboBox_device.addItem(port_name)
        else:
            if not self.comboBox_device.currentText() in [port.portName() for port in current_ports]:
                if self.com.portName() == self.comboBox_device.currentText():
                    if self.com.isOpen():
                        self.reset()

                        self.openDevice()
                    self.comboBox_device.removeItem(self.comboBox_device.currentIndex())
                    QMessageBox.information(self, '消息', '串口已拔出', QMessageBox.Yes)

            for port in current_ports:
                port_name = port.portName()
                if port_name not in [self.comboBox_device.itemText(i) for i in range(self.comboBox_device.count())]:
                    self.comboBox_device.addItem(port_name)

    def handle_ini_index_changed(self):
        item = self.comboBox_ini.currentText()
        file = QFile(item)
        if file.open(QIODevice.ReadOnly):
            content = file.readAll()
            self.Edit_ini.setText(content.data().decode())
            file.close()

    def open_ini(self):
        # 使用QFileDialog打开文件夹选择对话框
        filename = self.program_path + "\\" + self.comboBox_ini.currentText()
        print(filename)
        subprocess.Popen(['notepad.exe', filename])
