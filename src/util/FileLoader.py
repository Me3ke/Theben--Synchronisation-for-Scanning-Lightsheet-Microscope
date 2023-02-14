import os
import shutil
import logging
import importlib

log = logging.getLogger("log")

"""
"""


def load_setup(path):
    setup_name = os.path.basename(path)
    new_path = '.\\resources\\setups\\' + setup_name
    try:
        shutil.copy(path, new_path)
    except shutil.SameFileError:
        pass
    except PermissionError:
        log.error("No permission to copy files")
    try:
        setup_name_without_extension = setup_name.split('.')[0]
        import_path = "resources.setups." + setup_name_without_extension
        return importlib.import_module(import_path)
    except Exception as e:
        raise e
        # TODO custom exception?


def read_setup(path):
    file = open(path, 'r')
    return file.read()


def load_param(path):
    param_name = os.path.basename(path)
    new_path = '.\\resources\\params\\' + param_name
    try:
        shutil.copy(path, new_path)
    except shutil.SameFileError:
        pass
    except PermissionError:
        log.error("No permission to copy files")
    param_name_without_extension = param_name.split('.')[0]
    import_path = "resources.params." + param_name_without_extension
    return importlib.import_module(import_path)
