from GUIController import GUIController
"""

"""


class Commander:

    gui_controller = None

    def start_gui(self):
        # TODO möglicherweise in initialize übertragen
        self.gui_controller = GUIController()
        self.gui_controller.start_config_window()


commander = Commander()
commander.start_gui()
