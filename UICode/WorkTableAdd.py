"""code."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import Models.DataHandler as DH
import Models.SqlHandler as SQH
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, '..', 'UI', 'addWorkTable.ui')


class CreateWorkTable(QDialog):
    """Class."""

    data_signal = pyqtSignal(list)

    def __init__(self):
        """func."""
        super(CreateWorkTable, self).__init__()
        loadUi(UI_PATH, self)
        self.pochasRadioButton.toggled.connect(self.pochasTracking)
        self.usualRadioButton.toggled.connect(self.usualTableTracking)
        self.pchsPlusCheckBox.toggled.connect(self.pchsPlusTracking)
        self.sovmestCheckBox.toggled.connect(self.sovmestTracking)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.confirmButton.clicked.connect(self.on_ok)
        self._teachers_model = None
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def get_stvkaDljnst(self):
        """func."""
        current_index = self.fioComboBox.currentIndex()
        current_id = self._teachers_model.get_id(current_index)
        position = SQH.get_col_where(
            'doljnost', 'teacher_id', str(current_id), 'teachers')
        if not position or position[0] in (None, ""):
            return None
        rate = SQH.get_col_where(
            'stavka', 'doljnost', position[0], 'doljnosti')
        if not rate or rate[0] in (None, ""):
            return None
        return rate[0], current_id

    def on_ok(self):
        """func."""
        total = 0
        fio = self.fioComboBox.currentText()
        mainstavk = self.stavkaLineEdit.text()
        pochasOsn = self.pchsPlusLineEdit.text()
        sovmest = self.sovmestLineEdit.text()
        pochas = self.pochLineEdit.text()
        found = self.get_stvkaDljnst()
        if found is None:
            QMessageBox.warning(self, 'Ошибка', 'У должности нет ставки')
            return
        stvkaDljnst, prepod_id = found
        if self.usualRadioButton.isChecked():
            table_type = 'Обычная'
            rate, error = self._required_number(mainstavk, 'Введите ставку')
            if error:
                QMessageBox.warning(self, 'Ошибка', error)
                return
            total += rate * float(stvkaDljnst)
            extra, error = self._optional_number(pochasOsn)
            if error:
                QMessageBox.warning(self, 'Ошибка', error)
                return
            total += extra
            extra, error = self._optional_number(sovmest)
            if error:
                QMessageBox.warning(self, 'Ошибка', error)
                return
            total += extra * float(stvkaDljnst)
        elif self.pochasRadioButton.isChecked():
            table_type = 'Почасовая'
            hours, error = self._required_number(pochas, 'Введите часы')
            if error:
                QMessageBox.warning(self, 'Ошибка', error)
                return
            total = hours
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите тип таблицы')
            return
        list_to_send = [
            fio,
            prepod_id,
            table_type,
            mainstavk,
            pochas,
            pochasOsn,
            sovmest,
            total
        ]
        self.data_signal.emit(list_to_send)
        self.accept()

    def _required_number(self, text, empty_message):
        """func."""
        if not str(text).strip():
            return None, empty_message
        return DH.parse_non_negative_number(text)

    def _optional_number(self, text):
        """func."""
        if not str(text).strip():
            return 0, None
        return DH.parse_non_negative_number(text)

    def pchsPlusTracking(self):
        """func."""
        if self.pchsPlusCheckBox.isChecked():
            self.pchsPlusLineEdit.setReadOnly(False)
        else:
            self.pchsPlusLineEdit.setReadOnly(True)

    def sovmestTracking(self):
        """func."""
        if self.sovmestCheckBox.isChecked():
            self.sovmestLineEdit.setReadOnly(False)
        else:
            self.sovmestLineEdit.setReadOnly(True)

    def pochasTracking(self):
        """func."""
        self.stavkaLineEdit.setReadOnly(True)
        self.pochLineEdit.setReadOnly(False)
        self.pchsPlusLineEdit.setReadOnly(True)
        self.sovmestLineEdit.setReadOnly(True)
        self.pchsPlusCheckBox.setEnabled(False)
        self.sovmestCheckBox.setEnabled(False)
        self.pchsPlusCheckBox.setChecked(False)
        self.sovmestCheckBox.setChecked(False)
        self.stavkaLineEdit.clear()
        self.pchsPlusLineEdit.clear()
        self.sovmestLineEdit.clear()

    def usualTableTracking(self):
        """func."""
        self.stavkaLineEdit.setReadOnly(False)
        self.pochLineEdit.setReadOnly(True)
        self.pchsPlusCheckBox.setEnabled(True)
        self.sovmestCheckBox.setEnabled(True)
        self.pochLineEdit.clear()

    def set_teachers(self, model):
        """func."""
        self.fioComboBox.setModel(model)
        self._teachers_model = model

    def set_edit_lines(self, data):
        """func."""
        self.fioComboBox.setCurrentText(data[0])
        self.fioComboBox.setEditable(False)
        if data[2] == 'Обычная':
            self.usualRadioButton.setChecked(True)
        if data[2] == 'Почасовая':
            self.pochasRadioButton.setChecked(True)
        self.stavkaLineEdit.setText(str(data[3]))
        self.pochLineEdit.setText(str(data[4]))
        self.pchsPlusLineEdit.setText(str(data[5]))
        self.sovmestLineEdit.setText(str(data[6]))
