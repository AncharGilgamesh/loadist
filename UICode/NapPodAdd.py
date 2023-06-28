"""code."""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'addNapPod.ui')


class NapPodAdd(QDialog):
    """class."""

    data_signal = pyqtSignal(str, str)

    def __init__(self):
        """func."""
        super(NapPodAdd, self).__init__()
        loadUi('PartTwo/DiplomOldUI/Working/UI/addNapPod.ui', self)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.addNapPod.clicked.connect(self.on_ok)
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def on_ok(self):
        """func."""
        code = self.codeLineEdit.text()
        name = self.nameTextEdit.toPlainText()
        if not code:
            QMessageBox.warning(self, 'Ошибка', 'Добавьте код направления')
        if not name:
            QMessageBox.warning(
                self, 'Ошибка', 'Добавьте наименование направления')
        self.data_signal.emit(code, name)
        self.accept()
