import logging
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QObject, pyqtSignal

"""
inspired by https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
"""


# noinspection PyUnresolvedReferences
class QTextEditLogger(logging.Handler, QObject):

    append_text = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QTextEdit(parent)
        self.widget.setStyleSheet("background-color: white")
        self.widget.setReadOnly(True)
        self.append_text.connect(self.widget.append)
        self.widget.ensureCursorVisible()

    def emit(self, record):
        msg = self.format(record)
        self.append_text.emit(msg)
