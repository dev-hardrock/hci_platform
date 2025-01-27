from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtCore import QObject


def get_available_port():
    """获取可用的串口号"""
    ports = QSerialPortInfo.availablePorts()
    return ports


class SerialManager(QObject):
    def __init__(self, callback=None):
        super().__init__()
        # 回调函数
        self.callback = callback
        self.com = QSerialPort()

    def open(self, port, baudrate=115200, callback=None):
        """打开串口"""
        if self.is_open():
            raise Exception("串口已打开")  # 手动抛出异常
        # 设置串口属性
        self.com.setPortName(port)
        self.com.setBaudRate(baudrate)
        self.com.setDataBits(QSerialPort.Data8)
        self.com.setParity(QSerialPort.NoParity)
        self.com.setStopBits(QSerialPort.OneStop)
        self.com.setFlowControl(QSerialPort.NoFlowControl)

        # 添加接收信号
        self.com.readyRead.connect(self.read_data)

        # 打开串口
        if not self.com.open(QSerialPort.ReadWrite):
            raise Exception("串口打开失败")  # 手动抛出异常
        return

    def close(self):
        """关闭串口"""
        if self.is_open():
            self.com.close()

    def is_open(self):
        """检查串口是否打开"""
        return self.com is not None and self.com.isOpen()

    def read_data(self):
        """当有数据可读时触发,读取当前缓冲区内所有数据"""
        # return bytes
        data = self.com.readAll()
        # text = data.data().decode('utf-8')
        if self.callback:
            self.callback(data)

    def send_data(self, data):
        """发送数据"""
        chunk_size = 1024
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            bytes_written = self.com.write(chunk)
            if bytes_written == -1:
                print("Error writing to serial port")
                break
            self.com.flush(QSerialPort.Output)
