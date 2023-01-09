import time
import logging
import sys
import threading

from PyQt6.QtCore import QFile, QIODeviceBase
from gui.MainWindow import MainWindow
from gui.ConfigWindow import ConfigWindow
from PyQt6.QtWidgets import QApplication

log = logging.getLogger("log")

"""
"""


class GUIController:
    # TODO macht ein controller interface sinn?

    main_window = None
    config_window = None
    app = None
    mode = ""
    sequence = ""
    setup_path = ""
    param_path = ""

    def start_config_window(self):
        thread = threading.Thread(target=self.show_config_window, name='Config_Window')
        thread.start()
        time.sleep(1)

        self.config_window.add_subscriber_for_finished_check_event(self.start_main_window)

    def start_main_window(self):
        self.mode = self.config_window.mode
        self.sequence = self.config_window.sequence
        self.setup_path = self.config_window.setup_path
        self.param_path = self.config_window.param_path

        self.config_window.close()
        self.main_window = MainWindow()
        self.main_window.show()
        time.sleep(1)

        # TODO Verifikation wird durch das event onfinished check event aufgerufen
        # TODO die Verifikation sollte dann in einem eigenen Thread laufen und
        # TODO ausgaben im log geben. Erst danach wird der start button zum starten
        # TODO verwendet. Vorher sollte eine Message ausgegeben werden

        self.main_window.add_subscriber_for_start_event(self.theben)
        self.main_window.add_subscriber_for_save_event(self.save)
        # TODO hier muss überlegt werden welche klassen auf welche events reagieren

        self.test_log()

    def show_config_window(self):
        app = QApplication(sys.argv)
        # TODO rufe dann im commander die entsprechenden methoden auf als wäre stop gecallt worden
        app.aboutToQuit.connect(self.theben)
        self.config_window = ConfigWindow()
        sys.exit(app.exec())

    def theben(self):
        log.critical("goin manf")

    def save(self):
        pixmap = self.main_window.get_pixmap()
        path_to_file = self.main_window.save_image_path
        if path_to_file == "":
            log.error("No path specified")
        else:
            file = QFile(path_to_file)
            if file.open(QIODeviceBase.OpenModeFlag.WriteOnly):
                pixmap.save(file)
            else:
                log.error("File could not be opened, make sure the file is closed and files may be created")

    def test_log(self):
        log.debug('damn, a bug')
        log.info('something to remember')
        log.warning('that\'s not right')
        log.error('foobar')
        log.critical("theben")
