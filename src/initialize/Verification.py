import subprocess
import logging
import shutil
import os
import importlib

from src.util.FileLoader import *

"""

"""

log = logging.getLogger("log")


class Verification:

    commander = None
    setup = None
    param = None

    def __init__(self, mode, sequence, setup_path, param_path):
        self.mode = mode
        self.sequence = sequence
        self.setup_path = setup_path
        self.param_path = param_path

    def verify(self):
        self.setup = load_setup(self.setup_path)
        if self.mode == "running":
            pass
            # self.param = load_param(self.param_path)
        else:
            pass
            # TODO evtl. schon eine file für die params erstellen
        return self.setup

    def verify_hcontroller_connected(self):
        # TODO vielleicht check nach allen serialports (auch laser, kamera)
        process = subprocess.Popen(["powershell.exe", ".\\src\\util\\check_hcontroller.ps1",
                                    self.setup.serial_port_hc_1, self.setup.serial_port_hc_2], stdout=subprocess.PIPE)
        p_out, p_err = process.communicate()
        return_value = p_out.decode().strip()
        print(return_value)
        return return_value

    def check_hcontroller_program(self):
        pass

    def set_commander(self, commander):
        self.commander = commander
