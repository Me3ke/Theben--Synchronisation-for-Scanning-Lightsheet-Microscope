import logging

"""
inspired by https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""


class CustomFormatter(logging.Formatter):
    """
    Create a custom format for log entries.
    """

    grey = "<span style=\" font-size:8pt; font-weight:600; color:#808080;\" >"
    green = "<span style=\" font-size:8pt; font-weight:600; color:#008000;\" >"
    yellow = "<span style=\" font-size:8pt; font-weight:600; color:#888800;\" >"
    red = "<span style=\" font-size:8pt; font-weight:600; color:#ff0000;\" >"
    bold_red = "<span style=\" font-size:10pt; font-weight:800; color:#ff0000;\" >"
    reset = "</span>"
    format = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)

