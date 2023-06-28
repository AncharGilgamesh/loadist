"""Doljnosti."""

from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QLabel,\
      QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui


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
        self.ok_button = QPushButton("Ok", self)
        vbox.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel", self)
        vbox.addWidget(self.cancel_button)
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def on_ok(self):
        """func."""
        if not self.lineEdit1.text():
            QMessageBox.warning(self, "Error", "Пожалуйста, введите должность")
        elif not self.lineEdit2.text():
            QMessageBox.warning(self, "Error", "Пожалуйста, введите ставку")
        elif not self.lineEdit2.text().isdigit():
            QMessageBox.warning(self, "Error", "Ставка должна быть числом")
        else:
            self.submitted.emit(
                self.lineEdit1.text(), float(self.lineEdit2.text()))
            self.accept()
