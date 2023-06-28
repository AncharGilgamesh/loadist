"""code."""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'addDiscipline.ui')


class DisciplineAdd(QDialog):
    """class."""

    data_signal = pyqtSignal(str, str)

    def __init__(self):
        """func."""
        super(DisciplineAdd, self).__init__()
        loadUi(UI_PATH, self)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.addDisciplineButton.clicked.connect(self.on_ok)
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def on_ok(self):
        """func."""
        code = self.codeComboBox.currentText()
        name = self.disciplineTextEdit.toPlainText()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название дисциплины')
        self.data_signal.emit(code, name)

    def set_codes(self, model):
        """func."""
        self.codeComboBox.setModel(model)
