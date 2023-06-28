"""class."""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton,\
      QPushButton, QLabel
from PyQt5 import QtGui


class NameSelectionDialog(QDialog):
    """class."""

    def __init__(self, item_list):
        """func."""
        super().__init__()
        self.selected_item = None
        self.setWindowTitle("List Dialog")
        layout = QVBoxLayout()
        label = QLabel("Выберите аспиранта: ")
        label.setStyleSheet("font-size: 18px;")
        layout.addWidget(label)
        self.buttons = []
        for item in item_list:
            button = QRadioButton(item)
            button.setStyleSheet("font-size: 16px;")
            button.toggled.connect(self.on_button_toggled)
            layout.addWidget(button)
            self.buttons.append(button)
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("font-size: 16px;")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setLayout(layout)
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/other.png')))

    def on_button_toggled(self):
        """func."""
        for button in self.buttons:
            if button.isChecked():
                self.selected_item = button.text()

    def get_selected_item(self):
        """func."""
        return self.selected_item
