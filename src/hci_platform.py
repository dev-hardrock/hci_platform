import os
import subprocess
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QFile, QIODevice
from src.serialmanager import *
from src.serialmanager import SerialManager
from PyQt5.QtGui import QCursor, QIcon, QColor, QTextFormat
from generated.hci_platform import Ui_Hci_PlatForm
from src.utils import *
import json


# 继承两个父类
class Hci_PlatForm(QWidget, Ui_Hci_PlatForm):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        # 重命名上位机名称
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Hci_PlatForm", "Hci_PlatForm"))

        # 设置上位机图标
        self.setWindowIcon(QIcon("./resources/images/bt.svg"))

        # 获取当前程序执行路径
        self.topdir = os.path.realpath(os.path.dirname(sys.argv[0]))

        # 初始化
        self.isMousePressed = False
        self.com = SerialManager(callback=None)

        # 开启鼠标跟踪
        self.Edit_CmdList.viewport().setCursor(QCursor(Qt.ArrowCursor))

        # 查找上位机同级目录下测试文件
        self.ComboBox_TestFile_Init()

        # 加载测试文件信息
        self.ComboBox_TestFile_Load()

        # 初始化串口波特率配置
        self.ComboBox_SerialBaudList_Init()

        # 定义一个定时器，1s定时检测串口列表
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_serial_ports)
        self.connect_signals_slots()
        self.timer.start(1000)

    def ComboBox_TestFile_Load(self):
        """加载指令文件"""
        if not self.cur_file == "":
            with open(self.cur_file, 'r', encoding='utf-8') as file:
                cmdlist = json.load(file)
            self.Edit_CmdList.clear()
            for command in cmdlist['hci_commands']:
                if command['identifier'] == "Link Control Commands":
                    self.Edit_CmdList.append("--------  " + command['identifier'] + "  --------")
                    for cmd in command['command']:
                        self.Edit_CmdList.append(cmd['name'])

    def ComboBox_TestFile_Init(self):
        """查找可用的指令文件"""
        jsonfiles = find_files(self.topdir, ".json")
        for file in jsonfiles:
            self.ComboBox_TestFile.addItem(os.path.basename(file))
        self.cur_file = self.ComboBox_TestFile.currentText()

    def ComboBox_SerialBaudList_Init(self):
        """初始化串口波特率列表"""
        self.ComboBox_SerialBaudList.addItem("115200")
        self.ComboBox_SerialBaudList.addItem("921600")

    def connect_signals_slots(self):
        """连接信号与槽函数"""
        # 创建Btn_OpenFile单击事件处理信号
        self.Btn_OpenFile.clicked.connect(self.open_file)
        # 创建ComboBox_TestFile信号
        self.ComboBox_TestFile.currentIndexChanged.connect(self.ComboBox_TestFile_index_update)
        # 创建ComboBox_DeviceList处理信号
        self.ComboBox_DeviceList.activated.connect(self.refresh_serial_ports)
        # 创建Btn_OpenDevice单击事件处理信号
        self.Btn_OpenDevice.clicked.connect(self.openDevice)
        # 创建Btn_SendCmd单击事件处理信号
        self.Btn_SendCmd.clicked.connect(self.Btn_SendCmd_Click)
        # 创建Btn_Clear指令单击事件处理信号
        self.Btn_Clear.clicked.connect(self.Edit_CmdDetail_Clear)
        # 创建Edit_CmdList鼠标移动信号
        self.Edit_CmdList.mouseMoveEvent = self.cmdMouseMoveEvent
        # 创建Edit_CmdList鼠标按下信号
        self.Edit_CmdList.mousePressEvent = self.cmdMousePressEvent
        # 创建Edit_CmdList鼠标松开信号
        self.Edit_CmdList.mouseReleaseEvent = self.cmdMouseReleaseEvent
        # 创建Edit_CmdList鼠标双击信号
        self.Edit_CmdList.mouseDoubleClickEvent = self.cmdmouseDoubleClickEvent
        # 创建Edit_CmdProperty内容改变信号
        self.Edit_CmdProperty.textChanged.connect(self.Edit_CmdDetailShow)

    def Edit_CmdDetailShow(self):
        """16进制指令数据显示"""
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

    def Edit_CmdDetail_Clear(self):
        self.Edit_CmdDetail.clear()

    def cmdmouseDoubleClickEvent(self, event):
        """指令列表窗口鼠标双击事件处理函数"""
        return

    def cmdMouseReleaseEvent(self, event):
        """指令列表窗口鼠标释放事件处理函数"""
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
        """指令列表窗口鼠标按下事件处理函数"""
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
        """指令列表窗口鼠标移动事件处理函数"""
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

    def Btn_SendCmd_Click(self):
        """发送指令按键单机事件处理函数"""
        data = self.Edit_CmdDetail.toPlainText()
        self.Edit_Log.append(data)
        self.Edit_Log.ensureCursorVisible()
        if self.com.is_open():
            self.com.send_data(data)

    def openDevice(self):
        """打开设备按键单击处理函数"""
        text = self.Btn_OpenDevice.text()
        portName = self.ComboBox_DeviceList.currentText()
        portBaud = int(self.ComboBox_SerialBaudList.currentText())
        if text == "打开设备":
            if not portName == "":
                try:
                    self.com.open(portName, portBaud)
                    self.Btn_OpenDevice.setText("关闭设备")
                    self.ComboBox_DeviceList.setEnabled(False)
                except Exception as e:
                    QMessageBox.warning(self, '错误', str(e))
                    self.Btn_OpenDevice.setText("打开设备")
                    self.ComboBox_DeviceList.setEnabled(True)
            else:
                QMessageBox.warning(None, "警告", "请插入设备!")
        else:
            if not portName == "":
                self.com.close()
                self.Btn_OpenDevice.setText("打开设备")
                self.ComboBox_DeviceList.setEnabled(True)

    def refresh_serial_ports(self):
        """刷新可用串口号列表并填充到ComboBox中"""
        current_ports = get_available_port()
        if self.ComboBox_DeviceList.currentText() == "":
            # 添加comboBox_ini
            for port in current_ports:
                port_name = port.portName()
                self.ComboBox_DeviceList.addItem(port_name)
        else:
            if not self.ComboBox_DeviceList.currentText() in [port.portName() for port in current_ports]:
                if self.com.com.portName() == self.ComboBox_DeviceList.currentText():
                    if self.com.is_open():
                        self.com.close()
                        self.openDevice()
                    self.ComboBox_DeviceList.removeItem(self.ComboBox_DeviceList.currentIndex())
                    QMessageBox.information(self, '消息', '串口已拔出', QMessageBox.Yes)
            for port in current_ports:
                port_name = port.portName()
                if port_name not in [self.ComboBox_DeviceList.itemText(i) for i in range(self.ComboBox_DeviceList.count())]:
                    self.ComboBox_DeviceList.addItem(port_name)

    def ComboBox_TestFile_index_update(self):
        file_name = self.ComboBox_TestFile.currentText()
        file = QFile(file_name)
        if file.open(QIODevice.ReadOnly):
            self.cur_file = file_name
            self.ComboBox_TestFile_Load()
        else:
            QMessageBox.warning(self, '警告', '文件打开失败', QMessageBox.Yes)

    def open_file(self):
        # 使用QFileDialog打开文件夹选择对话框
        filename = self.topdir + "\\" + self.ComboBox_TestFile.currentText()
        # print(filename)
        subprocess.Popen(['notepad.exe', filename])

    def closeEvent(self, event):
        """关闭串口时确保关闭串口"""
        return super().closeEvent(event)



