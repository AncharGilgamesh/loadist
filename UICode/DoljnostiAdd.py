"""Диалог добавления должности."""

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

import Models.DataHandler as DH


class DoljnostAdd(QDialog):
    """class."""

    submitted = pyqtSignal(str, float)

    def __init__(self, parent=None):
        """func."""
        super(DoljnostAdd, self).__init__(parent)
        self.setWindowTitle("Добавить должность")
        self.setGeometry(200, 200, 300, 150)
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel("Введите должность:", self))
        self.lineEdit1 = QLineEdit(self)
        vbox.addWidget(self.lineEdit1)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Введите нагрузку на 1 ставку:", self))
        self.lineEdit2 = QLineEdit(self)
        hbox.addWidget(self.lineEdit2)
        vbox.addLayout(hbox)
        self.ok_button = QPushButton("ОК", self)
        vbox.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Отмена", self)
        vbox.addWidget(self.cancel_button)
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/Images/other.png")))

    def on_ok(self):
        """func."""
        if not self.lineEdit1.text():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите должность")
            return
        if not self.lineEdit2.text():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите ставку")
            return
        rate, error = DH.parse_non_negative_number(self.lineEdit2.text())
        if error:
            QMessageBox.warning(self, "Ошибка", error)
            return
        self.submitted.emit(self.lineEdit1.text(), rate)
        self.accept()
