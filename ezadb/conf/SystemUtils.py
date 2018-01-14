import platform
import os
import time


class SystemUtils:

    WINDOWS_OS = 'Windows'
    LINUX_OS = 'Linux'

    @staticmethod
    def os_name():
        """ Returns the system/OS name, e.g. 'Linux' or 'Windows'
                An empty string is returned if the value cannot be determined.
            """
        return platform.system()

    @staticmethod
    def generate_random_filename(extension):
        return '{timestamp}.{ext}'.format(timestamp=int(round(time.time() * 1000)), ext=extension)

    @staticmethod
    def os_based_path(path):
        """ Retrieve the correct path operating system independent """
        return os.path.expanduser(path)
