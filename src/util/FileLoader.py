import os
import shutil
import logging
import importlib

from src.Exceptions.FileImportException import FileImportException

log = logging.getLogger("log")


def load(path, specification):
    """
    Import a setup or param file from a path
    :param path: The path of the setup/param file
    :param specification: 'setup' or 'param' indicating whether it is a setup or param
    :raise FileImportException: if file is corrupted
    :return: The imported file, or None if no path is specified
    """
    if path == "":
        return None
    name = os.path.basename(path)
    if specification == 'setup':
        new_path = '.\\resources\\setups\\' + name
    else:
        new_path = '.\\resources\\params\\' + name
    if os.path.isfile(new_path):
        os.remove(new_path)
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
    try:
        with open(path, 'r') as file:
            return file.read()
    except PermissionError:
        log.error("No permission to read file")
    except Exception as ex:
        log.error(ex)


def save(path, text):
    """Save a string in a file"""
    try:
        with open(path, 'w') as file:
            file.write(text)
    except PermissionError:
        log.error("No permission to save in file")
    except Exception as ex:
        log.error(ex)





