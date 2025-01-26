import sys
from PyQt5.QtWidgets import QApplication
from src.hci_platform import Hci_PlatForm

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 窗口风格设置成windows系统风格
    app.setStyle('windows')
    hci_plateform = Hci_PlatForm()
    hci_plateform.show()
    sys.exit(app.exec())

