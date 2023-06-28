"""settings."""

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtGui
import os
import Models.SqlHandler as SQH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'generalSettings.ui')


class SettingsDialog(QDialog):
    """class."""

    def __init__(self):
        """func."""
        super(SettingsDialog, self).__init__()
        loadUi(UI_PATH, self)
        self.set_data()
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))
        self.readSettingsCheckBox.toggled.connect(self.settings_tracking)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.saveButton.clicked.connect(self.save_clicked)

    def set_data(self):
        """func."""
        data = SQH.select_settings()
        data = tuple(map(str, data[0]))
        if data:
            self.startStudyLineEdit.setText(data[0])
            self.endStudyLineEdit.setText(data[1])
            self.otdelLineEdit.setText(data[2])
            self.kafedraLineEdit.setText(data[3])
            self.magLimitLineEdit.setText(data[4])
            self.baqLimitLineEdit.setText(data[5])
            if data[6] != '0':
                self.startReadRowLineEdit.setText(data[6])
            if data[7] != '0':
                self.endReadRowLineEdit.setText(data[7])
            if data[8] != '0':
                self.startReadColLineEdit.setText(data[8])
            if data[9] != '0':
                self.endReadColLineEdit.setText(data[9])

    def settings_tracking(self):
        """func."""
        if self.readSettingsCheckBox.isChecked():
            self.startReadRowLineEdit.setReadOnly(False)
            self.endReadRowLineEdit.setReadOnly(False)
            self.startReadColLineEdit.setReadOnly(False)
            self.endReadColLineEdit.setReadOnly(False)
        else:
            self.startReadRowLineEdit.setReadOnly(True)
            self.endReadRowLineEdit.setReadOnly(True)
            self.startReadColLineEdit.setReadOnly(True)
            self.endReadColLineEdit.setReadOnly(True)
            self.startReadRowLineEdit.clear()
            self.endReadRowLineEdit.clear()
            self.startReadColLineEdit.clear()
            self.endReadColLineEdit.clear()

    def save_clicked(self):
        """func."""
        start_study = self.startStudyLineEdit.text()
        end_study = self.endStudyLineEdit.text()
        otdel = self.otdelLineEdit.text()
        kafedra = self.kafedraLineEdit.text()
        mag_lim = self.magLimitLineEdit.text()
        baq_lim = self.baqLimitLineEdit.text()
        start_read_row = self.startReadRowLineEdit.text()
        end_read_row = self.endReadRowLineEdit.text()
        start_read_col = self.startReadColLineEdit.text()
        end_read_col = self.endReadColLineEdit.text()
        if not start_read_row:
            start_read_row = 0
        if not end_read_row:
            end_read_row = 0
        if not start_read_col:
            start_read_col = 0
        if not end_read_col:
            end_read_col = 0
        if not start_study:
            start_study = ''
        if not end_study:
            end_study = ''
        if not otdel:
            otdel = ''
        if not kafedra:
            kafedra = ''
        if not mag_lim:
            mag_lim = 0
        if not baq_lim:
            baq_lim = 0
        list_to_save = [
            start_study,
            end_study,
            otdel,
            kafedra,
            mag_lim,
            baq_lim,
            start_read_row,
            end_read_row,
            start_read_col,
            end_read_col,
        ]
        SQH.insert_into_setting_table(list_to_save)
        self.accept()
