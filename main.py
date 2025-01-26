import sys
from PyQt5 import QtWidgets
from hci_platform_ui import Hci_PlatForm_Ui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # 窗口风格设置成windows系统风格
    app.setStyle('windows')
    hci_plateform = Hci_PlatForm_Ui()
    hci_plateform.show()
    sys.exit(app.exec())

