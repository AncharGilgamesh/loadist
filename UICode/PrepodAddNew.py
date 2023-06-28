"""code."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'prepodDialogNew.ui')


class PrepodAdd(QDialog):
    """Class."""

    data_signal = pyqtSignal(list)

    def __init__(self):
        """func."""
        super(PrepodAdd, self).__init__()
        loadUi(UI_PATH, self)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.confirmButton.clicked.connect(self.on_ok)
        self.curatorCheckBox.toggled.connect(self.curatorstvo_tracking)
        self.dipLimCheckBox.toggled.connect(self.dip_limit_tracking)
        self.addGroupButton.clicked.connect(self.add_group_cur)
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def curatorstvo_tracking(self):
        """func."""
        if self.curatorCheckBox.isChecked():
            self.addGroupButton.setEnabled(True)
        else:
            self.addGroupButton.setEnabled(False)

    def dip_limit_tracking(self):
        """func."""
        if self.dipLimCheckBox.isChecked():
            self.dipLimLineEdit.setReadOnly(False)
        else:
            self.dipLimLineEdit.setReadOnly(True)

    def on_ok(self):
        """func."""
        fio = self.fioLineEdit.text()
        zvanie = self.zvanieLineEdit.text()
        stepen = self.stepenLineEdit.text()
        doljnost = self.doljnostComboBox.currentText()
        dipLimit = self.dipLimLineEdit.text()
        curator = self.curatorLineEdit.text()
        list_to_send = [
            fio,
            zvanie,
            stepen,
            doljnost,
            dipLimit,
            curator
        ]
        if not fio:
            QMessageBox.warning(self, 'Ошибка', 'Введите ФИО')
            return
        words = fio.strip().split()
        if len(words) != 3:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Введите ФИО полностью (3 слова)')
            return
        self.data_signal.emit(list_to_send)
        self.accept()

    def add_group_cur(self):
        """func."""
        group = self.groupsComboBox.currentText()
        if self.curatorLineEdit.text():
            self.curatorLineEdit.setText(
                self.curatorLineEdit.text() + ', ' + group
            )
        else:
            self.curatorLineEdit.setText(group)

    def set_dljnsti(self, model):
        """func."""
        self.doljnostComboBox.setModel(model)

    def set_groups(self, model):
        """func."""
        self.groupsComboBox.setModel(model)

    def set_edit_lines(self, data):
        """func."""
        self.fioLineEdit.setText(data[0])
        self.zvanieLineEdit.setText(data[1])
        self.stepenLineEdit.setText(data[2])
        self.doljnostComboBox.setCurrentText(data[3])
        self.dipLimLineEdit.setText(str(data[4]))
        self.curatorLineEdit.setText(str(data[5]))
