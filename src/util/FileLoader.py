import os
import shutil
import logging
import importlib

from Exceptions.FileImportException import FileImportException

log = logging.getLogger("log")

"""

"""


def load(path, specification):
    """
    Import a setup or param file from a path
    :param path: The path of the setup/param file
    :param specification: 'setup' or 'param' indicating whether it is a setup or param
    :raise FileImportException: if file is corrupted
    :return: The imported file.
    """
    name = os.path.basename(path)
    if specification == 'setup':
        new_path = '.\\src\\resources\\setups\\' + name
    else:
        new_path = '.\\src\\resources\\params\\' + name
    try:
        # Load file into resources
        shutil.copy(path, new_path)
    except shutil.SameFileError:
        # Source and destination files are the same. Do nothing
        pass
    except PermissionError:
        log.error("No permission to copy files")
    try:
        # Filename is not allowed to contain '.' except for the extension
        name_without_extension = name.split('.')[0]
        if specification == 'setup':
            import_path = "resources.setups." + name_without_extension
        else:
            import_path = "resources.params." + name_without_extension
        # Returns the imported file
        return importlib.import_module(import_path)
    except Exception as ex:
        raise FileImportException(ex)


def read(path):
    """Return a String with the file content"""
    file = open(path, 'r')
    return file.read()


def save(path):
    pass
