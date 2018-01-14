#!/usr/bin/python
import os
import threading
import webbrowser

import pygubu

from ezadb import __version__
from ezadb import __AUTHOR__
from ezadb.EzADB import EzADB
from ezadb.conf.ConfigManager import ConfigManager
from ezadb.conf.I18n import Translator
from ezadb.conf.SystemUtils import SystemUtils
from ezadb.gui.PreviewImageDialog import PreviewImageDialog
from ezadb.utils.Log import Log
from ezadb.utils.Utils import Utils

try:
    import tkinter as tk  # for python 3
    from tkinter import *
    from tkinter import ttk
    from tkinter import filedialog
    import tkinter.font as tkFont

except:
    import Tkinter as tk  # for python 2
    import tkMessageBox as messagebox

# translator function
_ = Translator

# default app url
DEFAULT_URL = 'https://github.com/filipebatista/eZadb'


class EzADBGui(pygubu.TkApplication):
    def __init__(self, master):
        self.selected_device = None
        self.progress_dialog = None
        self.about_dialog = None
        self.appinfo_dialog = None
        self.configManager = ConfigManager()
        self.ezADB = EzADB(self.configManager.get_adb_path())
        pygubu.TkApplication.__init__(self, master)

    def _create_ui(self):
        # Create a builder
        self.builder = builder = pygubu.Builder(Translator)

        # Load an ui file
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'design_main.ui'))

        # Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainwindow', self.master)
        toplevel = self.master.winfo_toplevel()

        # Set main menu
        self.mainmenu = menu = builder.get_object('main_menu', toplevel)
        toplevel['menu'] = menu

        # Create ProgressBar
        s = ttk.Style()
        # s.theme_use("default")

        # custom properties for the progressbar
        s.configure("TProgressbar", thickness=15)

        # devices connected
        self.tree_devices = builder.get_object('treeview_devices', self.master)

        # devices connected item listener
        self.tree_devices.bind('<ButtonRelease-1>', self.on_treecolumn_device_click)
        self.tree_devices.bind('<Button-3>', self.rightClickCopyMenu)

        # device related buttons
        self.btn_reboot = builder.get_object('btn_device_reboot', self.master)
        self.btn_shutdown = builder.get_object('btn_device_shutdown', self.master)
        self.btn_screenshot = builder.get_object('btn_device_screenshot', self.master)

        # app related buttons
        self.btn_install = builder.get_object('btn_app_install', self.master)
        self.btn_uninstall = builder.get_object('btn_app_uninstall', self.master)
        self.btn_clear_data = builder.get_object('btn_app_clear_data', self.master)
        self.btn_pull_apk = builder.get_object('btn_app_pull_apk', self.master)
        self.btn_app_disable = builder.get_object('btn_app_disable', self.master)
        self.btn_app_info = builder.get_object('btn_app_info', self.master)

        # installed apps
        self.treeview_apps = builder.get_object('treeview_apps', self.master)
        self.treeview_apps.bind('<ButtonRelease-1>', self.on_treecolumn_apps_click)
        self.treeview_apps.bind('<Button-3>', self.rightClickCopyMenu)

        # set the callbacks
        builder.connect_callbacks(self)

        # set the app icon
        Utils.set_app_icon(toplevel)

    def _init_after(self):
        # initializes the value combo box only if we already have the adb path
        if self.configManager.get_adb_path() is not None:
            self.init_devices()
        else:
            self.ask_adb_path()

    def _create_progress_dialog(self):
        builder = pygubu.Builder(Translator)
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'progress_dialog.ui'))
        dialog = builder.get_object(
            'progressdialog', self.toplevel)
        # set dialog icon
        Utils.set_app_icon(dialog.toplevel)
        progressbar = builder.get_object('progressbar1')
        progressbar.start()
        return dialog

    def _center_dialog(self, dialog):
        """Adjust the dialog to center of parent window"""
        if dialog:
            # calculate middle point
            x = self.mainwindow.winfo_rootx()
            y = self.mainwindow.winfo_rooty()
            x = x + (self.mainwindow.winfo_width() / 2) - (dialog.toplevel.winfo_reqwidth() / 2)
            y = y + (self.mainwindow.winfo_height() / 2) - (dialog.toplevel.winfo_reqheight() / 2)
            geometry = '+{0}+{1}'.format(int(x), int(y))
            dialog.toplevel.geometry(geometry)

    def show_progress_dialog(self):
        def show():
            if self.progress_dialog is None:
                self.progress_dialog = self._create_progress_dialog()
                self.progress_dialog.run()
            else:
                self.progress_dialog.show()
            self._center_dialog(self.progress_dialog)

        self.mainwindow.after(100, show)

    def hide_progress_dialog(self):
        def hide():
            if self.progress_dialog:
                self.progress_dialog.close()

        self.mainwindow.after(100, hide)

    def ask_adb_path(self, initial_dir="/"):
        initial_dir = initial_dir if initial_dir is not None else "/"
        adbpath = filedialog.askopenfilename(title=_("Select ADB executable folder"),
                                             initialdir=os.path.dirname(initial_dir),
                                             parent=self.mainwindow)
        if adbpath:
            self.configManager.set_adb_path(adbpath)
            self.ezADB = EzADB(self.configManager.get_adb_path())
            self.init_devices()

    def init_devices(self):
        self.show_progress_dialog()
        if self.treeview_apps.get_children():
            self.treeview_apps.delete(*self.treeview_apps.get_children())
        if self.tree_devices.get_children():
            self.tree_devices.delete(*self.tree_devices.get_children())
        threading.Thread(target=self.load_devices).start()

    def load_devices(self):
        # clear previous list of Devices and Apps
        # self.delete_all_treeview_items(self.treeview_apps)
        # self.delete_all_treeview_items(self.tree_devices)
        devices = self.ezADB.get_devices()
        for val in devices:
            self.tree_devices.insert('', tk.END, iid=val, text=val, values=val, tags='treedevices')
        self.hide_progress_dialog()

    def on_treecolumn_device_click(self, event):
        item_selected = self.get_selected_tree_item(self.tree_devices)
        if item_selected:
            self.selected_device = item_selected
            self.enable_buttons([self.btn_reboot, self.btn_shutdown, self.btn_screenshot, self.btn_install])
            self.show_progress_dialog()
            threading.Thread(target=self.load_installed_apps).start()

    def on_treecolumn_apps_click(self, event):
        item_selected = self.get_selected_tree_item(self.treeview_apps)
        if item_selected:
            self.enable_buttons([self.btn_clear_data, self.btn_uninstall,
                                 self.btn_pull_apk, self.btn_app_disable, self.btn_app_info])
            self.show_progress_dialog()
            threading.Thread(target=self.get_app_state, args=[item_selected]).start()

    def get_app_state(self, item_selected):
        # invert the disable button text according to app current state
        if self.ezADB.get_app_state(self.selected_device, item_selected) == EzADB.State.ENABLED:
            app_disable_text = _('Disabled')
        else:
            app_disable_text = _('Enabled')

        def __callback__():
            self.btn_app_disable['text'] = app_disable_text
            self.hide_progress_dialog()

        self.mainwindow.after(100, __callback__)

    def on_reboot_click(self):
        self.ezADB.reboot_device(self.selected_device)

    def on_shutdown_click(self):
        self.ezADB.shutdown_device(self.selected_device)

    def on_uninstall_click(self):
        app_selected = self.get_selected_tree_item(self.treeview_apps)
        device_selected = self.get_selected_tree_item(self.tree_devices)
        self.ezADB.uninstall_app(device_selected, app_selected)
        self.on_treecolumn_device_click(None)

    def on_install_click(self):
        apk_file_path = filedialog.askopenfilename(title=_("Select APK to install"),
                                                   filetypes=(
                                                       ("Android Package File", "*.apk"), (_("All Files"), "*.*")),
                                                   parent=self.mainwindow)
        if apk_file_path:
            self.show_progress_dialog()
            threading.Thread(target=self.install_apk, args=[apk_file_path]).start()

    def install_apk(self, apk_file_path):
        self.ezADB.installAPK(self.selected_device, apk_file_path)
        Log.debug(self.__class__, "[on_install_click] {filepath}".format(filepath=apk_file_path))

        def __callback__():
            # reload the apps list
            self.on_treecolumn_device_click(None)
            self.hide_progress_dialog()

        self.mainwindow.after(100, __callback__)

    def on_cleardata_click(self):
        app_selected = self.get_selected_tree_item(self.treeview_apps)
        device_selected = self.get_selected_tree_item(self.tree_devices)
        self.ezADB.app_clear_data(device_selected, app_selected)
        self.on_treecolumn_device_click(None)

    def on_pull_apk_click(self):
        item_selected = self.get_selected_tree_item(self.treeview_apps)
        if item_selected:
            default_filename = str(item_selected).replace('.', '_') + ".apk"
            file_path = filedialog.asksaveasfilename(title=_('Save as...'),
                                                     initialfile=default_filename,
                                                     defaultextension=".apk",
                                                     filetypes=(
                                                         ("Android Package File", "*.apk"), (_("All Files"), "*.*")))
            self.show_progress_dialog()
            threading.Thread(target=self.pull_apk, args=(item_selected, file_path)).start()

    def on_app_menuitem_clicked(self, itemid):
        if itemid == 'subitem_settings':
            self.ask_adb_path(self.configManager.get_adb_path())
        if itemid == 'subitem_refresh_devices':
            self.init_devices()

    def on_screenshot_click(self):
        if self.selected_device:
            file_path = filedialog.asksaveasfilename(title=_("Save as..."),
                                                     initialfile=SystemUtils.generate_random_filename('png'),
                                                     defaultextension=".png",
                                                     filetypes=(
                                                         ("Portable Network Graphics", "*.png"),
                                                         (_("All Files"), "*.*")))
            self.show_progress_dialog()
            threading.Thread(target=self.get_screenshot, args=[file_path]).start()

    def on_disable_click(self):
        app_selected = self.get_selected_tree_item(self.treeview_apps)
        device_selected = self.get_selected_tree_item(self.tree_devices)
        current_app_state = self.ezADB.get_app_state(device_selected, app_selected)

        self.ezADB.enable_disable_app(device_selected, device_selected,
                                      EzADB.State.ENABLED if EzADB.State.DISABLED == current_app_state
                                      else EzADB.State.ENABLED)

    def on_show_info_click(self):
        app_selected = self.get_selected_tree_item(self.treeview_apps)
        self.show_progress_dialog()
        threading.Thread(target=self.get_app_info, args=[app_selected]).start()

    @staticmethod
    def get_selected_tree_item(tree_view):
        item_selected = tree_view.selection()
        if item_selected:
            return item_selected[0]
        return None

    def delete_all_treeview_items(self, tree_view):
        if tree_view:
            x = tree_view.get_children()
            Log.info(self.__class__, 'get_children values: ', x, '\n')
            if x != '()' or x != '\n':  # checks if there is something in the first row
                for child in x:
                    tree_view.delete(child)

    @staticmethod
    def enable_buttons(buttons):
        for btn in buttons:
            btn.config(state=tk.NORMAL)

    def load_installed_apps(self):
        # clear previous list if has any
        if self.treeview_apps.get_children():
            self.treeview_apps.delete(*self.treeview_apps.get_children())

        # get apps are installed in the device
        installed_apps = self.ezADB.get_applications_installed()
        for val in installed_apps:
            if val:
                self.treeview_apps.insert('', tk.END, iid=val, text=val, values=val, tags='treeapps')
        self.hide_progress_dialog()

    def pull_apk(self, app_selected, target_path):
        self.ezADB.pull_apk(app_selected, target_path, self.selected_device)
        self.hide_progress_dialog()
        Log.info(self.__class__, '[pull_apk]:{app}=>{target}'.format(app=app_selected, target=target_path))

    def get_screenshot(self, target_path):
        if target_path:
            self.ezADB.get_screenshot(self.selected_device, target_path)
            self.hide_progress_dialog()
            self.show_img_preview(target_path)

    def get_app_info(self, selected_app):
        self.show_progress_dialog()
        fullinfo = self.ezADB.get_app_info(self.selected_device, selected_app, True)
        lightinfo = self.ezADB.get_app_info(self.selected_device, selected_app)

        def __callback__():
            self.hide_progress_dialog()
            self.show_app_info_dialog(selected_app, fullinfo, lightinfo)

        self.master.after(100, __callback__)

    def show_img_preview(self, file_path):
        def open_preview():
            dialog = PreviewImageDialog(self.toplevel, file_path)
            self.mainwindow.wait_window(dialog.top)

        self.mainwindow.after(100, open_preview)

    def rightClickCopyMenu(self, event):
        """action in event of button 3 on tree view"""
        treeview = event.widget

        def copy_to_clipboard():
            self.master.clipboard_clear()
            # text to clipboard
            text_to_copy = self.get_selected_tree_item(treeview)
            self.master.clipboard_append(text_to_copy)

        menu = Menu(self.mainwindow, tearoff=0)
        menu.add_command(label="Copy", command=copy_to_clipboard)

        # select row under mouse
        iid = treeview.identify_row(event.y)
        if iid:
            # mouse pointer over item
            treeview.selection_set(iid)
            menu.post(event.x_root, event.y_root)
        else:
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
            pass

    # Help menu
    def on_help_menuitem_clicked(self, itemid):
        if itemid == 'help_online':
            webbrowser.open_new_tab(DEFAULT_URL)
        elif itemid == 'help_about':
            self.show_about_dialog()

    def show_about_dialog(self):
        if self.about_dialog is None:
            self.about_dialog = self._create_about_dialog()
            self.about_dialog.run()
        else:
            self.about_dialog.show()
        self._center_dialog(self.about_dialog)

    def _create_about_dialog(self):
        builder = pygubu.Builder(Translator)
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'about_dialog.ui'))

        dialog = builder.get_object('about_dialog', self.master.winfo_toplevel())
        Utils.set_app_icon(dialog.toplevel)
        # set version
        entry = builder.get_object('version')
        txt = entry.cget('text')
        txt = txt.replace('%version%', str(__version__))
        entry.configure(text=txt)
        # set authors
        entry = builder.get_object('copyr')
        txt = entry.cget('text')
        txt = txt.replace('%user1%', __AUTHOR__[0]['Name'])
        entry.configure(text=txt)

        def on_about_close_click():
            dialog.close()

        builder.connect_callbacks({'on_about_close_click': on_about_close_click})
        return dialog

    def show_app_info_dialog(self, selected_app, fullinfo, lightinfo):
        dialog_exists = self.appinfo_dialog is not None
        builder = pygubu.Builder(Translator)
        # create the dialog in the first time
        if not dialog_exists:
            builder.add_from_file(os.path.join(os.path.dirname(__file__), 'appinfo_dialog.ui'))
            self.appinfo_dialog = builder.get_object('appinfo_dialog', self.master.winfo_toplevel())
            Utils.set_app_icon(self.appinfo_dialog.toplevel)

        # set dialog title
        self.appinfo_dialog.toplevel.title('AppInfo for: ' + selected_app)

        # set the dialog with the application information
        text_fullinfo = builder.get_object('text_fullinfo')
        text_lightinfo = builder.get_object('text_lightinfo')
        # enable the controls
        text_fullinfo.config(state=NORMAL)
        text_lightinfo.config(state=NORMAL)
        # clear the previous text
        text_fullinfo.delete(1.0, tk.END)
        text_lightinfo.delete(1.0, tk.END)
        # add the new text
        text_fullinfo.insert(tk.END, fullinfo)
        text_lightinfo.insert(tk.END, lightinfo)

        def __show_select_copy_menu__(event):
            # define the call back for item click
            def __callback__(itemid):
                if itemid == 'copy':
                    self.master.clipboard_clear()
                    # text to clipboard
                    text_to_copy = event.widget.get(SEL_FIRST, SEL_LAST)
                    self.master.clipboard_append(text_to_copy)
                elif itemid == 'select_all':
                    """Select all text in the text widget"""
                    event.widget.tag_add(SEL, "1.0", END)
                    event.widget.focus_set()

            # create the menu to show
            menu = Menu(event.widget, tearoff=0)
            menu.add_command(label="Copy", command=lambda: __callback__('copy'))
            menu.add_command(label="Select All", command=lambda: __callback__('select_all'))
            menu.post(event.x_root, event.y_root)

        # make sure the widget gets focus when clicked
        # on, to enable highlighting and copying to the
        # clipboard.
        text_fullinfo.bind("<1>", lambda event: text_fullinfo.focus_set())
        text_lightinfo.bind("<1>", lambda event: text_lightinfo.focus_set())

        text_fullinfo.bind('<Button-3>', __show_select_copy_menu__)
        text_lightinfo.bind('<Button-3>', __show_select_copy_menu__)

        # disable the controls
        text_fullinfo.config(state=DISABLED)
        text_lightinfo.config(state=DISABLED)

        if not dialog_exists:
            self.appinfo_dialog.run()
        else:
            self.appinfo_dialog.show()
        self._center_dialog(self.appinfo_dialog)
