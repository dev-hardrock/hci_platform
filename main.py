import os.path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication
from hci_platform_ui import Hci_PlatForm_Ui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    hci_plateform = Hci_PlatForm_Ui()
    hci_plateform.show()
    sys.exit(app.exec())

