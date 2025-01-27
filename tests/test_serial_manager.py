import pytest
from unittest.mock import MagicMock, patch
from src.serialmanager import SerialManager
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort

# Mocking QSerialPort and QSerialPortInfo
# 创建 MockQSerialPort 模拟 QSerialPort 的行为
class MockQSerialPort:
    def __init__(self):
        self.is_open = False
        self.port_name = ""
        self.baud_rate = 0
        self.data_bits = None
        self.parity = None
        self.stop_bits = None
        self.flow_control = None
        self.readyRead = MagicMock()
        self.read_all_data = b""
        self.write_called_with = None

    def setPortName(self, port_name):
        """设置串口号"""
        self.port_name = port_name

    def setBaudRate(self, baud_rate):
        """设置串口波特率"""
        self.baud_rate = baud_rate

    def setDataBits(self, data_bits):
        """设置串口数据有效位"""
        self.data_bits = data_bits

    def setParity(self, parity):
        """设置奇偶位"""
        self.parity = parity

    def setStopBits(self, stop_bits):
        """设置停止位"""
        self.stop_bits = stop_bits

    def setFlowControl(self, flow_control):
        """设置流控"""
        self.flow_control = flow_control

    def open(self, mode):
        """打开串口"""
        self.is_open = True
        return True

    def close(self):
        """关闭串口"""
        self.is_open = False

    def isOpen(self):
        """检查串口是否已经打开"""
        return self.is_open

    def readAll(self):
        """读取所有数据"""
        data = self.read_all_data
        self.read_all_data = b""
        print(data)
        return data

    def write(self, data):
        """写入数据"""
        self.write_called_with = data
        return len(data)

    def flush(self, direction):
        pass

# 创建 MockQSerialPortInfo 类模拟 QSerialPortInfo 的行为
class MockQSerialPortInfo:
    @staticmethod
    def availablePorts():
        """获取可用的串口号"""
        return [
            MockQSerialPortInfo("/dev/ttyUSB0"),
            MockQSerialPortInfo("/dev/ttyUSB1")
        ]

    def __init__(self, port_name):
        """设置串口号"""
        self.port_name = port_name

    def device(self):
        """范围串口号"""
        return self.port_name


@pytest.fixture
def mock_qserialport(monkeypatch):
    # 将 QSerialPort 的 __init__ 替换成 MockQSerialPort.__init__
    monkeypatch.setattr(QSerialPort, '__init__', MockQSerialPort.__init__)
    # 将 QSerialPort 的 setPortName 替换成 MockQSerialPort.setPortName
    monkeypatch.setattr(QSerialPort, 'setPortName', MockQSerialPort.setPortName)
    monkeypatch.setattr(QSerialPort, 'setBaudRate', MockQSerialPort.setBaudRate)
    monkeypatch.setattr(QSerialPort, 'setDataBits', MockQSerialPort.setDataBits)
    monkeypatch.setattr(QSerialPort, 'setParity', MockQSerialPort.setParity)
    monkeypatch.setattr(QSerialPort, 'setStopBits', MockQSerialPort.setStopBits)
    monkeypatch.setattr(QSerialPort, 'setFlowControl', MockQSerialPort.setFlowControl)
    monkeypatch.setattr(QSerialPort, 'open', MockQSerialPort.open)
    monkeypatch.setattr(QSerialPort, 'close', MockQSerialPort.close)
    monkeypatch.setattr(QSerialPort, 'isOpen', MockQSerialPort.isOpen)
    monkeypatch.setattr(QSerialPort, 'readAll', MockQSerialPort.readAll)
    monkeypatch.setattr(QSerialPort, 'write', MockQSerialPort.write)
    monkeypatch.setattr(QSerialPort, 'flush', MockQSerialPort.flush)


@pytest.fixture
def mock_qserialportinfo(monkeypatch):
    # 将 QSerialPort 的 availablePorts 替换成 MockQSerialPort.availablePorts
    monkeypatch.setattr(QSerialPortInfo, 'availablePorts', MockQSerialPortInfo.availablePorts)


@pytest.fixture
def serial_manager(mock_qserialport, mock_qserialportinfo):
    manager = SerialManager()
    yield manager


def test_get_available_ports(serial_manager):
    """测试获取可用串口号的功能"""
    ports = serial_manager.get_available_port()
    assert len(ports) == 2
    assert ports[0].device() == "/dev/ttyUSB0"
    assert ports[1].device() == "/dev/ttyUSB1"


def test_open_and_close(serial_manager):
    """测试打开和关闭串口的功能。"""
    serial_manager.open("/dev/ttyUSB0", baudrate=9600)
    assert serial_manager.com.port_name == "/dev/ttyUSB0"
    assert serial_manager.com.baud_rate == 9600
    assert serial_manager.com.data_bits == QSerialPort.Data8
    assert serial_manager.com.parity == QSerialPort.NoParity
    assert serial_manager.com.stop_bits == QSerialPort.OneStop
    assert serial_manager.com.flow_control == QSerialPort.NoFlowControl
    assert serial_manager.com.isOpen() is True

    # Test closing the serial port
    serial_manager.close()
    assert serial_manager.com.isOpen() is False


def test_open_already_open(serial_manager):
    """测试在串口已经打开的情况下再次打开时抛出异常"""
    serial_manager.open("/dev/ttyUSB0", baudrate=9600)
    with pytest.raises(Exception) as exc_info:
        serial_manager.open("/dev/ttyUSB1", baudrate=9600)
    assert str(exc_info.value) == "Serial port already open."


def test_fail_to_open(serial_manager, mock_qserialport):
    """测试打开串口失败的情况"""

    # Manually create a QSerialPort instance to simulate failure
    # serial_manager.com = QSerialPort()

    # Modify the mock to simulate a failure when opening the serial port
    def mock_open(mode):
        return False

    # Use monkeypatch to replace the open method of the current com instance
    with patch.object(QSerialPort, 'open', side_effect=mock_open):
        with pytest.raises(Exception) as exc_info:
            serial_manager.open("/dev/ttyUSB0", baudrate=9600)
    assert str(exc_info.value) == "Failed to open serial port."  # Ensure correct spelling


def test_is_open(serial_manager):
    """测试检查串口是否打开的功能"""
    serial_manager.open("/dev/ttyUSB0", baudrate=9600)
    assert serial_manager.is_open() is True

    serial_manager.close()
    assert serial_manager.is_open() is False


def test_read_data(serial_manager):
    """测试从串口读取数据并调用回调函数的功能"""
    callback_mock = MagicMock()
    serial_manager.open("/dev/ttyUSB0", baudrate=9600, callback=callback_mock)
    serial_manager.com.read_all_data = b"Test Data\n"

    # 模拟 readyRead 信号
    # serial_manager.com.readyRead.emit()
    serial_manager.read_data()

    callback_mock.assert_called_once_with(b"Test Data\n")


def test_send_data(serial_manager):
    """测试向串口写入数据的功能"""
    serial_manager.open("/dev/ttyUSB0", baudrate=9600)
    serial_manager.send_data(b"Hello, World!")

    assert serial_manager.com.write_called_with == b"Hello, World!"



