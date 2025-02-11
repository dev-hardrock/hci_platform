from abc import ABC, abstractmethod
from typing import Type
import logging

logger = logging.getLogger(__name__)

HCI_NONE = 0
HCI_CMD = 1
HCI_ACL = 2
HCI_SCO = 3
HCI_EVT = 4
HCI_ISO = 5


# 定义一个类型
class Hci_Drv(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send(self) -> None:
        """
        抽象方法，留给子类重构
        """
        pass

    @abstractmethod
    def recv(self) -> None:
        """
        抽象方法，留给子类重构
        """
        pass


class Hci_Thread:
    def __init__(self, drv) -> None:
        self.txbuf = None
        self.tx_type = HCI_NONE
        self.hci_drv = drv

    def hci_tx_thread(self):
        if self.txbuf:
            self.hci_drv.send(self.txbuf)
            logger.info(f"{self.get_packet_type_str(self.txbuf[0], True)}{' '.join(f'{byte:02x}' for byte in self.txbuf)}")

    def hci_rx_thread(self):
        pass

    @staticmethod
    def get_packet_type_str(hci_type, issue):
        if issue:
            if hci_type == HCI_CMD:
                return "CMD => "
            elif hci_type == HCI_ACL:
                return "ACL => "
            elif HCI_SCO == HCI_SCO:
                return "ACL => "
            elif HCI_EVT == HCI_EVT:
                return "EVT => "
            elif HCI_ISO == HCI_ISO:
                return "ISO => "
            else:
                return "Unknown =>"
        else:
            if hci_type == HCI_CMD:
                return "CMD <= "
            elif hci_type == HCI_ACL:
                return "ACL <= "
            elif HCI_SCO == HCI_SCO:
                return "ACL <= "
            elif HCI_EVT == HCI_EVT:
                return "EVT <= "
            elif HCI_ISO == HCI_ISO:
                return "ISO <= "
            else:
                return "Unknown <="
