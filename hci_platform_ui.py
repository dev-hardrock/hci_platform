import os
import subprocess
import sys
import re
import serial.tools.list_ports
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtSerialPort import QSerialPortInfo
from hci_platform import Ui_Form
import serial


# 继承两个父类
def find_files(directory='', extersion=''):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn if f.endswith(extersion)]


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

        self.port_list = 0
        self.com = 0

        # 获取当前程序执行路径
        self.program_path = os.path.realpath(os.path.dirname(sys.argv[0]))

        # 添加创建comboBox_ini元素
        ini_files = find_files(self.program_path, ".ini")
        for file in ini_files:
            self.comboBox_ini.addItem(os.path.basename(file))

        # 添加串口波特率
        self.comboBox_serialBaud.addItem("115200")
        self.comboBox_serialBaud.addItem("921600")

        # 定义一个定时器，1s定时检测串口列表
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_serial_ports)
        self.connect_signals_slots()
        self.timer.start(1000)

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

    def openDevice(self):
        text = self.btn_openDevice.text()
        if text == "打开设备":
            self.btn_openDevice.setText("关闭设备")
            self.comboBox_device.setEnabled(False)
        else:
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
                com = serial.Serial(self.comboBox_device.currentText(), self.comboBox_serialBaud.currentText())
                if not com == "":
                    if com.is_open:
                        com.close()
                        self.openDevice()
                self.comboBox_device.removeItem(self.comboBox_device.currentIndex())
                QMessageBox.information(self, '消息', '串口已拔出', QMessageBox.Yes)

            for port in current_ports:
                port_name = port.portName()
                if port_name not in [self.comboBox_device.itemText(i) for i in range(self.comboBox_device.count())]:
                    self.comboBox_device.addItem(port_name)

    def handle_ini_index_changed(self):
        item = self.comboBox_ini.currentText()
        self.Edit_ini.setText(item)

    def open_ini(self):
        # 使用QFileDialog打开文件夹选择对话框
        filename = self.program_path + "\\" + self.comboBox_ini.currentText()
        print(filename)
        subprocess.Popen(['notepad.exe', filename])
