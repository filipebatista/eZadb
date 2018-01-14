import os

from .Config import Config
from ezadb.utils.Log import Log

try:
    from shutil import which
except ImportError:
    from backports.shutil_which import which

ADB_DEFAULT_NAME = 'adb'
DEFAULT_CONFIG_FOLDER = ".ezadb/config"
DEFAULT_CONFIG_FILENAME = "config.cfg"


class ConfigManager:
    def __init__(self):
        self.userDir = os.path.expanduser('~')
        config_folder = os.path.normpath("{userpath}/{default_folder}".format(userpath=self.userDir,
                                                                              default_folder=DEFAULT_CONFIG_FOLDER))
        self.configFilePath = config_folder + os.path.sep + DEFAULT_CONFIG_FILENAME
        # create the folders if they don't exist
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)

        self.config = Config(self.configFilePath)

        # try to set the adb if needed
        self._find_adb_path()

    def set_adb_path(self, path):
        """Set the path for the adb executable"""

        default_section = self.config.get_section('default')
        default_section.set('ADB_PATH', path)
        self.config.save_changes()

    def get_adb_path(self):
        """Get the adb executable path"""

        return self.config.get_section('default').get('ADB_PATH')

    def _find_adb_path(self):
        # check if we already defined the adb path
        if self.get_adb_path() is None:
            # try to find the adb executable in the path
            adb_full_path = which(ADB_DEFAULT_NAME)
            if adb_full_path is not None:
                self.set_adb_path(adb_full_path)
        else:
            Log.info(self.__class__, "ADB path already defined {path}".format(path=self.get_adb_path()))
