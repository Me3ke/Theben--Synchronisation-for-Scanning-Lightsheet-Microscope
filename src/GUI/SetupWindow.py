"""

"""

import logging
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *

ICON_NAME = './resources/thebenlogo.jpg'
WINDOW_TITLE = "Theben: Setup Window"
BACKGROUND_COLOR = "#C4CEFF"
DEFAULT_BOX_HEIGHT = 35
DEFAULT_BOX_WIDTH = 300

log = logging.getLogger("log")


class SetupWindow(QDialog):

    def __init__(self, path, setup):
        self.path = path
        self.setup = setup
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.init_layout()

    def init_layout(self):
        pass
