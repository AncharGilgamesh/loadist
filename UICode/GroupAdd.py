"""code."""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import Models.DataHandler as DH
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'addGroup.ui')


class GroupAdd(QDialog):
    """class."""

    data_signal = pyqtSignal(str, str, str, str)

    def __init__(self):
        """func."""
        super(GroupAdd, self).__init__()
        loadUi(UI_PATH, self)
        self.addGroupButton.clicked.connect(self.on_ok)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.aspirantCheckBox.toggled.connect(self.aspirantTracking)
        self.setWindowTitle('Добавить группу')
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def aspirantTracking(self):
        """func."""
        if self.aspirantCheckBox.isChecked():
            self.groupLineEdit.setText('асп')
            self.groupLineEdit.setReadOnly(True)
        else:
            self.groupLineEdit.clear()
            self.groupLineEdit.setReadOnly(False)

    def on_ok(self):
        """func."""
        groupNumber = self.groupLineEdit.text()
        amountOfStudents = self.amountLineEdit.text()
        curator = ''
        code = self.codeComboBox.currentText()
        if self.curatorCheckBox.isChecked():
            curator = self.prepodsComboBox.currentText()
        if not groupNumber:
            QMessageBox.warning(self, 'Ошибка', 'Введите номер группы')
            return
        if not amountOfStudents:
            QMessageBox.warning(self, 'Ошибка', 'Введите количество студентов')
            return
        amount, error = DH.parse_non_negative_number(
            amountOfStudents, integer=True)
        if error:
            QMessageBox.warning(self, 'Ошибка', error)
            return
        self.data_signal.emit(groupNumber, str(amount), curator, code)
        self.accept()

    def set_curators(self, model):
        """func."""
        self.prepodsComboBox.setModel(model)

    def set_codes(self, model):
        """func."""
        self.codeComboBox.setModel(model)
