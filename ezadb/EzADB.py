import subprocess

from conf.SystemUtils import SystemUtils
from utils.Log import Log
from utils.Utils import Utils

try:
    from enum import Enum
    from shutil import which
except ImportError:
    from enum import Enum
    from backports.shutil_which import which


class EzADB:
    def __init__(self, adb_path):
        # try to find the adb executable in the path
        if adb_path:
            self.__fullADBPath__ = SystemUtils.os_based_path(adb_path)

    def get_devices(self):
        """  Retrieve the list of connected devices

            Returns:
                the list of android devices that are attached """
        result = self.__execute_adb_cmd__('devices').decode()
        result = Utils.replace_all(result, {'\r': '', 'package:': ''}).splitlines()
        # pop the title item
        result.pop(0)
        result = list(filter(None, result))
        # remove the word device
        result = [w.replace('device', '') for w in result]
        return result

    def get_applications_installed(self):
        result = self.__execute_adb_cmd__('shell pm list packages').decode().replace('package:', '')
        result = result.splitlines()
        # pop the title item
        result.pop(0)
        result = list(filter(None, result))
        return result

    def installAPK(self, device_id=None, apk_full_path=None):
        """Performs the installation of an APK file"""
        if apk_full_path is None:
            Log.warn(self.__class__, 'The supplied path of apk is invalid')
            return

        command = 'install {apkpath}'.format(apkpath=apk_full_path)

        result = self.__execute_adb_cmd__(command)
        Log.info(self.__class__, result, device_id)

    def uninstall_app(self, device_id=None, package_name=None):
        """Performs the uninstall of an application """
        if package_name is None:
            Log.warn(self.__class__, 'The supplied PackageName is invalid')
            return

        command = "uninstall {package}".format(package=package_name)

        result = self.__execute_adb_cmd__(command, device_id)
        Log.info(self.__class__, result.decode())

    def enable_disable_app(self, device_id, package_name, app_state):
        """Enables/Disables a certain application/component """
        if package_name is None:
            Log.warn(self.__class__, 'The supplied PackageName is invalid')
            return

        # Type checking
        if not isinstance(app_state, EzADB.State):
            raise TypeError('appState must be an instance of State Enum')

        command = "shell pm {state} {package}" \
            .format(state="enable" if EzADB.State.ENABLED == app_state else "disable", package=package_name)

        result = self.__execute_adb_cmd__(command, device_id)
        Log.info(self.__class__, result.decode())

    def get_app_state(self, device_id=None, package_name=None):
        """Check is a certain application is enabled"""
        if package_name is None:
            Log.warn(self.__class__, 'The supplied PackageName is invalid')
            return

        command = "shell pm list packages -e {package}".format(package=package_name)

        result = self.__execute_adb_cmd__(command, device_id).decode()
        filtered_apps = Utils.replace_all(result, {'\r': '', 'package:': ''}).splitlines()

        if package_name in filtered_apps:
            return EzADB.State.ENABLED
        else:
            return EzADB.State.DISABLED

    def input_text(self, text):
        """Inserts a certain text string in the application selected field
               currently running on the device"""
        return self.__execute_adb_cmd__('shell input text ' + text)

    def open_url(self, url):
        """Opens a certain

             :param url: the url that should be open """
        return self.__execute_adb_cmd__('shell am start -a android.intent.action.VIEW -d ' + url)

    def set_permission(self, package_name, permission_name, perm_type):
        """ Grants or Revokes a certain permission for a specific application"""
        # Type checking
        if not isinstance(perm_type, EzADB.Permission):
            raise TypeError('permission must be an instance of Permission Enum. Received:{invalid}'
                            .format(invalid=perm_type))

        if perm_type == EzADB.Permission.GRANT:
            permission_type = 'grant'
        else:
            permission_type = 'revoke'

        return self.__execute_adb_cmd__("shell pm {permissionType} {package} {permissionName} "
                                        .format(permissionType=permission_type, package=package_name,
                                                permissionName=permission_name))

    def pull_file(self, file_name, target_dir, device_id):
        """Pulls a specific file from the device"""

        command = "pull {file_path} {target_path}".format(file_path=file_name, target_path=target_dir)
        Log.info(self.__class__, command)
        return self.__execute_adb_cmd__(command, device_id, True)

    def pull_apk(self, package_name, target_dir, device_id):
        """Pulls the APK of a certain application from the device"""
        apk_full_path = self._get_apk_full_path(device_id, package_name)
        return self.pull_file(apk_full_path, target_dir, device_id)

    def reboot_device(self, device_id):
        """Reboots a specific device"""
        return self.__execute_adb_cmd__("reboot", device_id)

    def shutdown_device(self, device_id):
        """Shutdown a specific device"""
        return self.__execute_adb_cmd__("shell reboot -p", device_id)

    def app_clear_data(self, device_id, package_name):
        """Clear the application of a specific application"""
        self.__execute_adb_cmd__("shell pm clear {app}".format(app=package_name), device_id)

    def get_screenshot(self, device_id, target_dir):
        """ Take a ScreenShot of a device display"""
        # create a unique temp filename based on the timestamp
        temp_filename = '/sdcard/{random_name}'.format(random_name=SystemUtils.generate_random_filename('png'))
        command = 'shell screencap -p {filename}'.format(filename=temp_filename)

        # make the screen dump to the device
        self.__execute_adb_cmd__(command, device_id, True)
        # pull the file from the device to the target dir selected
        self.pull_file(temp_filename, target_dir, device_id)
        # deletes the temp file from the device
        self._delete_file(temp_filename, device_id)

    def get_app_info(self, device_id, package_name, full_info=False):
        """Get system state associated with the given PACKAGE"""
        if package_name is None:
            Log.warn(self.__class__, 'The supplied PackageName is invalid')
            return
        if full_info:
            command = "shell pm dump {package}".format(package=package_name)
        else:
            command = "shell dumpsys package {package}".format(package=package_name)
        return self.__execute_adb_cmd__(command, device_id)

    def __execute_adb_cmd__(self, command, device_id=None, ignore_output=False):
        """ Executes a certain adb command

            :param command: the adb command to be executed """

        # append device id if exists
        if device_id is not None:
            command = '-s {device} {cmd}'.format(device=device_id, cmd=command)

        # start the adb server if needed
        self._start_adb_server()

        # remove spaces and split command into a list
        args = command.rstrip().split()
        # insert the adb path to the beginning of the list
        args.insert(0, self.__fullADBPath__)

        if ignore_output:
            proc = subprocess.Popen(args)
            proc.wait()
        else:
            return subprocess.check_output(args)

    def _delete_file(self, file_path, device_id):
        """ Deletes a specific file from the device"""
        self.__execute_adb_cmd__('shell rm {file_path}'.format(file_path=file_path), device_id, True)

    def _start_adb_server(self):
        """Check whether the adb server process is running."""
        subprocess.call([self.__fullADBPath__, 'start-server'])

    def _get_apk_full_path(self, device_id, package_name):
        apk_full_path = self.__execute_adb_cmd__(
            "shell pm path {package}".format(package=package_name), device_id) \
            .decode().replace('package:', '').rstrip()
        return apk_full_path

    class Permission(Enum):
        """ Enum for the Application permissions"""
        GRANT = 0
        REVOKE = 1

    class State(Enum):
        """ Enum for the Application state"""
        DISABLED = 0
        ENABLED = 1
