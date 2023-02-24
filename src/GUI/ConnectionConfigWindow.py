from PyQt6 import QtGui
from PyQt6.QtWidgets import *

ICON_NAME = './resources/thebenlogo.jpg'
BACKGROUND_COLOR = "#C4CEFF"


class ConnectionConfigWindow(QWidget):
    def __init__(self, box_list, label_list, title_text, caption_text, sub_caption_text, parent):
        super().__init__()
        self.setWindowTitle(title_text)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        if "laser" in title_text:
            self.type = 'laser'
        else:
            self.type = 'hc'

        caption = QLabel(self)
        caption.setText(caption_text)
        caption.setFont(QtGui.QFont('Arial', 15))

        sub_caption = QLabel(self)
        sub_caption.setText(sub_caption_text)
        sub_caption.setFont(QtGui.QFont('Arial', 11))
        sub_caption.setStyleSheet("color: Yellow")

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.close)
        button_box.rejected.connect(lambda: parent.reject(self.type))

        layout_form = QFormLayout()

        for i in range(0, len(label_list)):
            layout_form.addRow(label_list[i], box_list[i])

        layout_buttons = QVBoxLayout()
        layout_buttons.addWidget(button_box)

        layout_outer = QVBoxLayout()
        layout_outer.addWidget(caption)
        layout_outer.addWidget(sub_caption)
        layout_outer.addLayout(layout_form)
        layout_outer.addLayout(layout_buttons)

        self.setLayout(layout_outer)

        self.show()
        self.activateWindow()
