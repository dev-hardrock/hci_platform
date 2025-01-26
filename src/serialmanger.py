from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtCore import QObject

class SerialManger(QObject):
    def __init__(self):
        super().__init__()
        self.com = None

    def get_available_port(self):
        """获取可用的串口号"""
        ports = QSerialPortInfo.availablePorts()
        return ports

    def open(self, port, baudrate=115200, callback=None):
        """打开串口"""
        if self.com and self.com.isOpen():
            raise Exception("Serial port already open.")    # 手动抛出异常
        self.com = QSerialPort()
        # 设置串口属性
        self.com.setPortName(port)
        self.com.setBaudRate(baudrate)
        self.com.setDataBits(QSerialPort.Data8)
        self.com.setParity(QSerialPort.NoParity)
        self.com.setStopBits(QSerialPort.OneStop)
        self.com.setFlowControl(QSerialPort.NoFlowControl)

        # 回调函数
        self.callback = callback

        # 添加接收信号
        self.com.readyRead.connect(self.read_data)

        # 打开串口
        if not self.com.open(QSerialPort.ReadWrite):
            raise Exception("Failt to open serial port.")    # 手动抛出异常
        return

    def close(self):
        """关闭串口"""
        if self.com and self.com.isOpen():
            self.com.close()

    def is_open(self):
        """检查串口是否打开"""
        return self.com is not None and self.com.isOpen()


    def read_data(self):
        """当有数据可读时触发,读取当前缓冲区内所有数据"""
        data = self.com.readAll()
        text = data.data().decode('utf-8')
        if self.callback:
            self.callback(text)

    def send_data(self, tx_data):
        """发送数据"""
        if self.com.isOpen():
            self.com.write(tx_data)
            self.com.flush(QSerialPort.Output)