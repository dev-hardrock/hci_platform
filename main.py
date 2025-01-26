import os
import subprocess
import sys
import serial.tools.list_ports
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QTimer, QFile, QIODevice
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtGui import QCursor, QIcon, QColor, QTextFormat
from hci_platform import Ui_Hci_PlatForm
import json
import serial


# 继承两个父类
def find_files(directory='', extersion=''):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn if
            f.endswith(extersion)]


def convert_hex_string(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string
    # 将16进制字符串转成整数
    value = int(hex_string, 16)
    byte_list = []
    while value > 0:
        byte = value & 0xff
        byte_list.append(f"{byte:02x}")
        value >>= 8
    result = ' '.join(byte_list)
    return result


def find_serial_port():
    port_lists = []
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        port_lists.append(port)
    return port_lists


class Hci_PlatForm(QWidget, Ui_Hci_PlatForm):
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
        self.Edit_CmdList.viewport().setCursor(QCursor(Qt.ArrowCursor))

        # 添加创建comboBox_ini元素
        ini_files = find_files(self.program_path, ".json")
        for file in ini_files:
            self.ComboBox_TestFile.addItem(os.path.basename(file))
        item = self.ComboBox_TestFile.currentText()
        if not item == "":
            with open(item, 'r', encoding='utf-8') as file:
                data = json.load(file)
            for command in data['hci_commands']:
                if command['identifier'] == "Link Control Commands":
                    self.Edit_CmdList.append("--------  " + command['identifier'] + "  --------")
                    for cmd in command['command']:
                        self.Edit_CmdList.append(cmd['name'])
        # 添加串口波特率
        self.ComboBox_SerialBaudList.addItem("115200")
        self.ComboBox_SerialBaudList.addItem("921600")

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
        # 创建Btn_OpenFile单击事件处理信号
        self.Btn_OpenFile.clicked.connect(self.open_ini)
        # 创建ComboBox_TestFile信号
        self.ComboBox_TestFile.currentIndexChanged.connect(self.handle_ini_index_changed)
        # 创建ComboBox_DeviceList处理信号
        self.ComboBox_DeviceList.activated.connect(self.refresh_serial_ports)
        # 创建Btn_OpenDevice单击事件处理信号
        self.Btn_OpenDevice.clicked.connect(self.openDevice)
        # 创建Btn_SendCmd单击事件处理信号
        self.Btn_SendCmd.clicked.connect(self.send_hci_command)
        # 创建Btn_Clear指令单击事件处理信号
        self.Btn_Clear.clicked.connect(self.clear_hci_command)
        # 创建Edit_CmdList鼠标移动信号
        self.Edit_CmdList.mouseMoveEvent = self.cmdMouseMoveEvent
        # 创建Edit_CmdList鼠标按下信号
        self.Edit_CmdList.mousePressEvent = self.cmdMousePressEvent
        # 创建Edit_CmdList鼠标松开信号
        self.Edit_CmdList.mouseReleaseEvent = self.cmdMouseReleaseEvent
        # 创建Edit_CmdList鼠标双击信号
        self.Edit_CmdList.mouseDoubleClickEvent = self.cmdmouseDoubleClickEvent
        # 创建Edit_CmdProperty内容改变信号
        self.Edit_CmdProperty.textChanged.connect(self.cmdHexDataShow)

    def cmdHexDataShow(self):
        text_content = self.Edit_CmdProperty.toPlainText()
        # print(text_content)
        try:
            # 字符串格式转换成json格式
            json_data = json.loads(text_content)
            # 获取所有键值， 键值个数正常为1
            all_keys = json_data.keys()
            if len(all_keys) == 1:
                json_file = self.ComboBox_TestFile.currentText()
                if not json_file == "":
                    with open(json_file, 'r', encoding='utf-8') as file:
                        hci_info = json.load(file)
                    for identifier in hci_info['hci_commands']:
                        for command in identifier['command']:
                            for key in all_keys:
                                if command['name'] == key:
                                    self.Edit_CmdDetail.clear()
                                    opcode = convert_hex_string(command['opcode'])
                                    if opcode is None:
                                        return
                                    # params =
                                    print(opcode)
                                    # message += hex_string
                                    # self.Edit_cmdData.append()
                                    self.Edit_CmdDetail.append(opcode)
        except json.JSONDecodeError as e:
            return

    def cmdmouseDoubleClickEvent(self, event):
        return

    def cmdMouseReleaseEvent(self, event):
        self.isMousePressed = False
        cursor = self.Edit_CmdList.cursorForPosition(event.pos())
        # 获取光标所在行数
        line = cursor.block().blockNumber()
        # print(line)
        # 检查点击是否在最后一行之后的空白区域
        text_height = 0
        for i in range(self.Edit_CmdList.document().blockCount()):
            block_geometry = self.Edit_CmdList.document().documentLayout().blockBoundingRect(
                self.Edit_CmdList.document().findBlockByNumber(i))
            text_height += block_geometry.height()
        if event.pos().y() <= text_height:
            if line >= 0:
                cmd = cursor.block().text()
                json_file = self.ComboBox_TestFile.currentText()
                if not json_file == "":
                    with open(json_file, 'r', encoding='utf-8') as file:
                        hci_info = json.load(file)
                    for identifier in hci_info['hci_commands']:
                        for command in identifier['command']:
                            if command['name'] == cmd:
                                # self.Edit_cmd.clear()
                                if 'parameters' in command:
                                    data = {}
                                    for parameter in command['parameters']:
                                        data[parameter['name']] = 0
                                    json_data = {command['name']: data}
                                    json_array = json.dumps(json_data, indent=4)
                                    # print(json_array)
                                    """
                                    Output example: {
                                        "HCI_Inquiry":{
                                            "LAP": 0,
                                            "Inquiry_Length": 0,
                                            "Num_Responses": 0
                                        }
                                    }
                                    """
                                    self.Edit_CmdProperty.setText(json_array)
                                else:
                                    json_data = {command['name']: 0}
                                    json_array = json.dumps(json_data, indent=4)
                                    self.Edit_CmdProperty.setText(json_array)

    def cmdMousePressEvent(self, event):
        extra_selections = []
        selection = self.Edit_CmdList.ExtraSelection()
        # 获取光标
        selection.cursor = self.Edit_CmdList.cursorForPosition(event.pos())
        # 获取光标所在行数
        line = selection.cursor.block().blockNumber()
        # print(line)
        # 检查点击是否在最后一行之后的空白区域
        text_height = 0
        for i in range(self.Edit_CmdList.document().blockCount()):
            block_geometry = self.Edit_CmdList.document().documentLayout().blockBoundingRect(
                self.Edit_CmdList.document().findBlockByNumber(i))
            text_height += block_geometry.height()
        if event.pos().y() <= text_height:
            if line >= 0:
                line_color = QColor(0, 120, 215)
                selection.format.setBackground(line_color)
                selection.format.setForeground(QColor("white"))
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor.clearSelection()
                extra_selections.append(selection)
                self.Edit_CmdList.setExtraSelections(extra_selections)
        self.isMousePressed = True

    def cmdMouseMoveEvent(self, event):
        if self.isMousePressed:
            extra_selections = []
            selection = self.Edit_CmdList.ExtraSelection()
            # 获取当前文本光标位置
            selection.cursor = self.Edit_CmdList.cursorForPosition(event.pos())
            # 文本光标移动到当前行的起始位置
            line = selection.cursor.block().blockNumber()
            # print(line)
            # 检查点击是否在最后一行之后的空白区域
            text_height = 0
            for i in range(self.Edit_CmdList.document().blockCount()):
                block_geometry = self.Edit_CmdList.document().documentLayout().blockBoundingRect(
                    self.Edit_CmdList.document().findBlockByNumber(i))
                text_height += block_geometry.height()
            if event.pos().y() <= text_height:
                if line >= 0:
                    line_color = QColor(0, 120, 215)
                    selection.format.setBackground(line_color)
                    selection.format.setForeground(QColor("white"))
                    selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                    selection.cursor.clearSelection()
                    extra_selections.append(selection)
                    self.Edit_CmdList.setExtraSelections(extra_selections)

    def clear_hci_command(self):
        self.Edit_CmdDetail.clear()

    def send_hci_command(self):
        tx_data = self.Edit_CmdDetail.toPlainText()
        self.Edit_Log.append(tx_data)
        self.Edit_Log.ensureCursorVisible()
        if self.com.isOpen():
            self.com.write(tx_data)
            self.com.flush(QSerialPort.Output)

    def openDevice(self):
        text = self.Btn_OpenDevice.text()
        portName = self.ComboBox_DeviceList.currentText()
        portBaud = int(self.ComboBox_SerialBaudList.currentText())
        if text == "打开设备":
            self.Btn_OpenDevice.setText("关闭设备")
            self.ComboBox_DeviceList.setEnabled(False)
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
                        self.Btn_OpenDevice.setText("打开设备")
                        self.ComboBox_DeviceList.setEnabled(True)
                        return
                except:
                    QMessageBox.critical(self, '错误', "设备打开失败!")
                    self.Btn_OpenDevice.setText("打开设备")
                    self.ComboBox_DeviceList.setEnabled(True)
                    return

            else:
                QMessageBox.information(None, "警告", "请插入设备!")
                self.Btn_OpenDevice.setText("打开设备")
                self.ComboBox_DeviceList.setEnabled(True)
        else:
            if not portName == "":
                self.com.close()
            self.Btn_OpenDevice.setText("打开设备")
            self.ComboBox_DeviceList.setEnabled(True)

    def refresh_serial_ports(self):
        """刷新可用串口号列表并填充到ComboBox中"""
        current_ports = QSerialPortInfo.availablePorts()
        if self.ComboBox_DeviceList.currentText() == "":
            # 添加comboBox_ini
            for port in current_ports:
                port_name = port.portName()
                self.ComboBox_DeviceList.addItem(port_name)
        else:
            if not self.ComboBox_DeviceList.currentText() in [port.portName() for port in current_ports]:
                if self.com.portName() == self.ComboBox_DeviceList.currentText():
                    if self.com.isOpen():
                        self.reset()

                        self.openDevice()
                    self.ComboBox_DeviceList.removeItem(self.ComboBox_DeviceList.currentIndex())
                    QMessageBox.information(self, '消息', '串口已拔出', QMessageBox.Yes)

            for port in current_ports:
                port_name = port.portName()
                if port_name not in [self.ComboBox_DeviceList.itemText(i) for i in range(self.ComboBox_DeviceList.count())]:
                    self.ComboBox_DeviceList.addItem(port_name)

    def handle_ini_index_changed(self):
        item = self.ComboBox_TestFile.currentText()
        file = QFile(item)
        if file.open(QIODevice.ReadOnly):
            content = file.readAll()
            self.Edit_CmdList.setText(content.data().decode())
            file.close()

    def open_ini(self):
        # 使用QFileDialog打开文件夹选择对话框
        filename = self.program_path + "\\" + self.ComboBox_TestFile.currentText()
        # print(filename)
        subprocess.Popen(['notepad.exe', filename])





if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 窗口风格设置成windows系统风格
    app.setStyle('windows')
    hci_plateform = Hci_PlatForm()
    hci_plateform.show()
    sys.exit(app.exec())

