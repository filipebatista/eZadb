#!/usr/bin/python -u

import argparse
import os
import sys

import errno
from builtins import input
from conf.ConfigManager import ConfigManager

# from EzADB import EzADB
from ezadb.EzADB import EzADB
from ezadb import __version__

PERMISSION_TYPE_GRANT = 'GRANT'
PERMISSION_TYPE_REVOKE = 'REVOKE'
PERMISSIONS_LIST = [PERMISSION_TYPE_GRANT, PERMISSION_TYPE_REVOKE]

parser = argparse.ArgumentParser(description="eZadb ADB - use adb like a boss!",
                                 epilog="GNU General Public License v3.0")

# default group options
main_group = parser.add_argument_group('default options')
sub_maingroup = main_group.add_mutually_exclusive_group()
sub_maingroup.add_argument('-d', '--devices', action='store_true')
sub_maingroup.add_argument('-t', '--inputText', dest='inputText')
sub_maingroup.add_argument('-u', '--uninstall', dest='uninstall',
                           help='Uninstall a specific application indicating the package name')
sub_maingroup.add_argument('-i', '--install', dest='install',
                           help='Install a specific application indicating the full path of the apk')
sub_maingroup.add_argument('-sc', '--screenshot_path', dest="screenshot_path",
                           help='Take a ScreenShot of a device display')
sub_maingroup.add_argument('-url', dest="url_link",
                           help='Opens a specific URL in the device')

group = parser.add_argument_group('permissions', description='Define permissions of an application')
group.add_argument('--package', help='Package name of the application')
group.add_argument('--permission', help='Android Permission to be set')
group.add_argument('--type', help='Type of permission', choices=PERMISSIONS_LIST)
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__,
                    help='Print the version number and exit')
args = parser.parse_args()

configManager = ConfigManager()
ezADB = EzADB(configManager.get_adb_path())


def show_app_menu(apps_list):
    """Show the list of applications installed in the device"""
    os.system('clear')
    print(30 * "-", "Select the Application", 30 * "-")
    menu = {}
    for index, app in enumerate(apps_list):
        menu[index] = app
    # add an exit option
    menu[len(menu)] = "Exit"
    loop = True
    while loop:
        for index, app in enumerate(menu):
            if index == len(menu) - 1:
                print("[{}]: Exit ".format(index))
            else:
                print("[{}]: Application: {}".format(index, menu[index]))
        choice = int(input("Enter your choice[{}-{}]:".format(0, (len(menu) - 1))))

        if choice > (len(menu) - 1):
            print("\n Not Valid Choice Try again")
        elif choice == (len(menu) - 1):
            sys.exit(0)
            # This will make the while loop to end as not value of loop is set to False
        else:
            return menu[choice]


def ask_adb_path():
    """Ask the user to input the full path of the ADB file"""

    full_path = input("Please enter the ADB full path (e.g.: ~/android-sdk/platform-tools/adb): ")
    if os.path.exists(full_path):
        configManager.set_adb_path(full_path)
    else:
        print("The file ADB path entered does not exist")
        sys.exit(errno.ENOENT)


def main():
    # check if the adb is defined
    if not configManager.get_adb_path():
        ask_adb_path()

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    if len(ezADB.get_devices()) > 0:
        if args.devices:
            print('List of devices attached')
            devices = ezADB.get_devices()
            for idx, device in enumerate(devices):
                print("[{}]:Device: {} \n".format(idx, device))
        elif args.inputText:
            print(ezADB.input_text(args.inputText))
        elif args.uninstall:
            print(ezADB.uninstall_app(None, args.uninstall))
        elif args.install:
            print(ezADB.installAPK(None, args.install))
        elif args.screenshot_path:
            ezADB.get_screenshot(None, args.screenshot_path)
        elif args.package or args.permission or args.type:
            if all([args.permission, args.type]):
                application = args.package
                # no application defined retrieve from the menu
                if application is None:
                    application = show_app_menu(ezADB.get_applications_installed())
                permission_type = EzADB.Permission.GRANT if (
                    args.type.lower() == PERMISSION_TYPE_GRANT.lower()) else EzADB.Permission.REVOKE
                ezADB.set_permission(application, args.permission, permission_type)
            else:
                raise parser.error("Package, permission and type all must be set ")
        elif args.url_link:
            ezADB.open_url(args.url_link)
    else:
        print('No devices attached')


if __name__ == "__main__":
    main()
