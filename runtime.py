#!/usr/bin/env python

import binascii
import contextlib
import hashlib
import io
import os
import re
import shutil
import sqlite3 as sl
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
import json
from datetime import datetime

import requests
import wx
from packaging.version import parse
from platformdirs import *

from constants import *

verbose = False
adb = None
fastboot = None
adb_sha256 = None
fastboot_sha256 = None
phones = []
phone = None
advanced_options = False
update_check = True
firmware_model = None
firmware_id = None
custom_rom_id = None
logfile = None
pumlfile = None
sdk_version = None
image_mode = None
image_path = None
custom_rom_file = None
message_box_title = None
message_box_message = None
version = None
db = None
boot = None
system_code_page = None
codepage_setting = False
codepage_value = ''
magisk_package = ''
file_explorer = ''
linux_shell = ''
patched_with = ''
customize_font = False
pf_font_face = ''
pf_font_size = 12
app_labels = {}
a_only = False
offer_patch_methods = False
use_busybox_shell = False
firmware_hash_valid = False
firmware_has_init_boot = False
rom_has_init_boot = False
dlg_checkbox_values = None
recovery_patch = False
config_path = None

# ============================================================================
#                               Class Boot
# ============================================================================
class Boot():
    def __init__(self):
        self.boot_id = None
        self.boot_hash = None
        self.boot_path = None
        self.is_patched = None
        self.magisk_version = None
        self.hardware = None
        self.boot_epoch = None
        self.package_id = None
        self.package_boot_hash = None
        self.package_type = None
        self.package_sig = None
        self.get_package_path = None
        self.package_epoch = None


# ============================================================================
#                               Function get_boot
# ============================================================================
def get_boot():
    global boot
    return boot


# ============================================================================
#                               Function set_boot
# ============================================================================
def set_boot(value):
    global boot
    boot = value


# ============================================================================
#                               Function get_labels
# ============================================================================
def get_labels():
    global app_labels
    return app_labels


# ============================================================================
#                               Function set_labels
# ============================================================================
def set_labels(value):
    global app_labels
    app_labels = value


# ============================================================================
#                               Function get_patched_with
# ============================================================================
def get_patched_with():
    global patched_with
    return patched_with


# ============================================================================
#                               Function set_patched_with
# ============================================================================
def set_patched_with(value):
    global patched_with
    patched_with = value


# ============================================================================
#                               Function get_db
# ============================================================================
def get_db():
    global db
    return db


# ============================================================================
#                               Function set_db
# ============================================================================
def set_db(value):
    global db
    db = value


# ============================================================================
#                               Function get_boot_images_dir
# ============================================================================
def get_boot_images_dir():
    # boot_images did not change at version 5, so we can keep on using 4
    if parse(VERSION) < parse('4.0.0'):
        return 'boot_images'
    else:
        return 'boot_images4'


# ============================================================================
#                               Function get_factory_images_dir
# ============================================================================
def get_factory_images_dir():
    # factory_images only changed after version 5
    if parse(VERSION) < parse('6.0.0'):
        return 'factory_images'
    else:
        return 'factory_images6'


# ============================================================================
#                               Function get_pf_db
# ============================================================================
def get_pf_db():
    # we have different db schemas for each of these versions
    if parse(VERSION) < parse('4.0.0'):
        return 'PixelFlasher.db'
    elif parse(VERSION) < parse('6.0.0'):
        return 'PixelFlasher4.db'
    else:
        return 'PixelFlasher6.db'


# ============================================================================
#                               Function get_verbose
# ============================================================================
def get_verbose():
    global verbose
    return verbose


# ============================================================================
#                               Function set_verbose
# ============================================================================
def set_verbose(value):
    global verbose
    verbose = value


# ============================================================================
#                               Function get_a_only
# ============================================================================
def get_a_only():
    global a_only
    return a_only


# ============================================================================
#                               Function set_a_only
# ============================================================================
def set_a_only(value):
    global a_only
    a_only = value


# ============================================================================
#                               Function get_adb
# ============================================================================
def get_adb():
    global adb
    return adb


# ============================================================================
#                               Function set_adb
# ============================================================================
def set_adb(value):
    global adb
    adb = value


# ============================================================================
#                               Function get_fastboot
# ============================================================================
def get_fastboot():
    global fastboot
    return fastboot


# ============================================================================
#                               Function set_fastboot
# ============================================================================
def set_fastboot(value):
    global fastboot
    fastboot = value


# ============================================================================
#                               Function get_adb_sha256
# ============================================================================
def get_adb_sha256():
    global adb_sha256
    return adb_sha256


# ============================================================================
#                               Function set_adb_sha256
# ============================================================================
def set_adb_sha256(value):
    global adb_sha256
    adb_sha256 = value


# ============================================================================
#                               Function get_fastboot_sha256
# ============================================================================
def get_fastboot_sha256():
    global fastboot_sha256
    return fastboot_sha256


# ============================================================================
#                               Function set_fastboot_sha256
# ============================================================================
def set_fastboot_sha256(value):
    global fastboot_sha256
    fastboot_sha256 = value


# ============================================================================
#                               Function get_phones
# ============================================================================
def get_phones():
    global phones
    return phones


# ============================================================================
#                               Function set_phones
# ============================================================================
def set_phones(value):
    global phones
    phones = value


# ============================================================================
#                               Function get_phone
# ============================================================================
def get_phone():
    global phone
    return phone


# ============================================================================
#                               Function set_phone
# ============================================================================
def set_phone(value):
    global phone
    phone = value


# ============================================================================
#                               Function get_system_codepage
# ============================================================================
def get_system_codepage():
    global system_code_page
    return system_code_page


# ============================================================================
#                               Function set_system_codepage
# ============================================================================
def set_system_codepage(value):
    global system_code_page
    system_code_page = value


# ============================================================================
#                               Function get_codepage_setting
# ============================================================================
def get_codepage_setting():
    global codepage_setting
    return codepage_setting


# ============================================================================
#                               Function set_codepage_setting
# ============================================================================
def set_codepage_setting(value):
    global codepage_setting
    codepage_setting = value


# ============================================================================
#                               Function get_codepage_value
# ============================================================================
def get_codepage_value():
    global codepage_value
    return codepage_value


# ============================================================================
#                               Function set_codepage_value
# ============================================================================
def set_codepage_value(value):
    global codepage_value
    codepage_value = value


# ============================================================================
#                               Function get_pf_font_face
# ============================================================================
def get_pf_font_face():
    global pf_font_face
    return pf_font_face


# ============================================================================
#                               Function set_pf_font_face
# ============================================================================
def set_pf_font_face(value):
    global pf_font_face
    pf_font_face = value


# ============================================================================
#                               Function get_pf_font_size
# ============================================================================
def get_pf_font_size():
    global pf_font_size
    return pf_font_size


# ============================================================================
#                               Function set_pf_font_size
# ============================================================================
def set_pf_font_size(value):
    global pf_font_size
    pf_font_size = value


# ============================================================================
#                               Function get_customize_font
# ============================================================================
def get_customize_font():
    global customize_font
    return customize_font


# ============================================================================
#                               Function set_customize_font
# ============================================================================
def set_customize_font(value):
    global customize_font
    customize_font = value


# ============================================================================
#                               Function get_magisk_package
# ============================================================================
def get_magisk_package():
    global magisk_package
    return magisk_package


# ============================================================================
#                               Function set_magisk_package
# ============================================================================
def set_magisk_package(value):
    global magisk_package
    magisk_package = value


# ============================================================================
#                               Function get_file_explorer
# ============================================================================
def get_file_explorer():
    global file_explorer
    return file_explorer


# ============================================================================
#                               Function set_file_explorer
# ============================================================================
def set_file_explorer(value):
    global file_explorer
    file_explorer = value


# ============================================================================
#                               Function get_linux_shell
# ============================================================================
def get_linux_shell():
    global linux_shell
    return linux_shell


# ============================================================================
#                               Function set_linux_shell
# ============================================================================
def set_linux_shell(value):
    global linux_shell
    linux_shell = value


# ============================================================================
#                               Function get_advanced_options
# ============================================================================
def get_advanced_options():
    global advanced_options
    return advanced_options


# ============================================================================
#                               Function set_advanced_options
# ============================================================================
def set_advanced_options(value):
    global advanced_options
    advanced_options = value


# ============================================================================
#                               Function get_patch_methods_settings
# ============================================================================
def get_patch_methods_settings():
    global offer_patch_methods
    return offer_patch_methods


# ============================================================================
#                               Function set_patch_methods_settings
# ============================================================================
def set_patch_methods_settings(value):
    global offer_patch_methods
    offer_patch_methods = value


# ============================================================================
#                               Function get_recovery_patch_settings
# ============================================================================
def get_recovery_patch_settings():
    global recovery_patch
    return recovery_patch


# ============================================================================
#                               Function get_recovery_patch_settings
# ============================================================================
def set_recovery_patch_settings(value):
    global recovery_patch
    recovery_patch = value


# ============================================================================
#                               Function get_use_busybox_shell_settings
# ============================================================================
def get_use_busybox_shell_settings():
    global use_busybox_shell
    return use_busybox_shell


# ============================================================================
#                               Function set_use_busybox_shell_settings
# ============================================================================
def set_use_busybox_shell_settings(value):
    global use_busybox_shell
    use_busybox_shell = value


# ============================================================================
#                               Function get_update_check
# ============================================================================
def get_update_check():
    global update_check
    return update_check


# ============================================================================
#                               Function set_update_check
# ============================================================================
def set_update_check(value):
    global update_check
    update_check = value


# ============================================================================
#                               Function get_firmware_hash_validity
# ============================================================================
def get_firmware_hash_validity():
    global firmware_hash_valid
    return firmware_hash_valid


# ============================================================================
#                               Function set_firmware_hash_validity
# ============================================================================
def set_firmware_hash_validity(value):
    global firmware_hash_valid
    firmware_hash_valid = value


# ============================================================================
#                               Function get_firmware_has_init_boot
# ============================================================================
def get_firmware_has_init_boot():
    global firmware_has_init_boot
    return firmware_has_init_boot


# ============================================================================
#                               Function set_firmware_has_init_boot
# ============================================================================
def set_firmware_has_init_boot(value):
    global firmware_has_init_boot
    firmware_has_init_boot = value


# ============================================================================
#                               Function get_rom_has_init_boot
# ============================================================================
def get_rom_has_init_boot():
    global rom_has_init_boot
    return rom_has_init_boot


# ============================================================================
#                               Function set_rom_has_init_boot
# ============================================================================
def set_rom_has_init_boot(value):
    global rom_has_init_boot
    rom_has_init_boot = value


# ============================================================================
#                               Function get_dlg_checkbox_values
# ============================================================================
def get_dlg_checkbox_values():
    global dlg_checkbox_values
    return dlg_checkbox_values


# ============================================================================
#                               Function set_dlg_checkbox_values
# ============================================================================
def set_dlg_checkbox_values(value):
    global dlg_checkbox_values
    dlg_checkbox_values = value


# ============================================================================
#                               Function get_firmware_model
# ============================================================================
def get_firmware_model():
    global firmware_model
    return firmware_model


# ============================================================================
#                               Function set_firmware_model
# ============================================================================
def set_firmware_model(value):
    global firmware_model
    firmware_model = value


# ============================================================================
#                               Function get_firmware_id
# ============================================================================
def get_firmware_id():
    global firmware_id
    return firmware_id


# ============================================================================
#                               Function set_firmware_id
# ============================================================================
def set_firmware_id(value):
    global firmware_id
    firmware_id = value


# ============================================================================
#                               Function get_custom_rom_id
# ============================================================================
def get_custom_rom_id():
    global custom_rom_id
    return custom_rom_id


# ============================================================================
#                               Function set_custom_rom_id
# ============================================================================
def set_custom_rom_id(value):
    global custom_rom_id
    custom_rom_id = value


# ============================================================================
#                               Function get_logfile
# ============================================================================
def get_logfile():
    global logfile
    return logfile


# ============================================================================
#                               Function set_logfile
# ============================================================================
def set_logfile(value):
    global logfile
    logfile = value


# ============================================================================
#                               Function get_pumlfile
# ============================================================================
def get_pumlfile():
    global pumlfile
    return pumlfile


# ============================================================================
#                               Function set_pumlfile
# ============================================================================
def set_pumlfile(value):
    global pumlfile
    pumlfile = value


# ============================================================================
#                               Function get_sdk_version
# ============================================================================
def get_sdk_version():
    global sdk_version
    return sdk_version


# ============================================================================
#                               Function set_sdk_version
# ============================================================================
def set_sdk_version(value):
    global sdk_version
    sdk_version = value


# ============================================================================
#                               Function get_image_mode
# ============================================================================
def get_image_mode():
    global image_mode
    return image_mode


# ============================================================================
#                               Function set_image_mode
# ============================================================================
def set_image_mode(value):
    global image_mode
    image_mode = value


# ============================================================================
#                               Function get_image_path
# ============================================================================
def get_image_path():
    global image_path
    return image_path


# ============================================================================
#                               Function set_image_path
# ============================================================================
def set_image_path(value):
    global image_path
    image_path = value


# ============================================================================
#                               Function get_custom_rom_file
# ============================================================================
def get_custom_rom_file():
    global custom_rom_file
    return custom_rom_file


# ============================================================================
#                               Function set_custom_rom_file
# ============================================================================
def set_custom_rom_file(value):
    global custom_rom_file
    custom_rom_file = value


# ============================================================================
#                               Function get_message_box_title
# ============================================================================
def get_message_box_title():
    global message_box_title
    return message_box_title


# ============================================================================
#                               Function set_message_box_title
# ============================================================================
def set_message_box_title(value):
    global message_box_title
    message_box_title = value


# ============================================================================
#                               Function get_message_box_message
# ============================================================================
def get_message_box_message():
    global message_box_message
    return message_box_message


# ============================================================================
#                               Function set_message_box_message
# ============================================================================
def set_message_box_message(value):
    global message_box_message
    message_box_message = value


# ============================================================================
#                               Function puml
# ============================================================================
def puml(message='', left_ts = False, mode='a'):
    with open(get_pumlfile(), mode, encoding="ISO-8859-1", errors="replace") as puml_file:
        puml_file.write(message)
        if left_ts:
            puml_file.write(f"note left:{datetime.now():%Y-%m-%d %H:%M:%S}\n")


# ============================================================================
#                               Function init_config_path
# ============================================================================
def init_config_path():
    config_path = get_sys_config_path()
    set_config_path(config_path)
    with contextlib.suppress(Exception):
        file_path = os.path.join(config_path, CONFIG_FILE_NAME)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="ISO-8859-1", errors="replace") as f:
                data = json.load(f)
                f.close()
            pf_home = data['pf_home']
            if pf_home and os.path.exists(pf_home):
                set_config_path(pf_home)
    config_path = get_config_path()
    if not os.path.exists(os.path.join(config_path, 'logs')):
        os.makedirs(os.path.join(config_path, 'logs'), exist_ok=True)
    if not os.path.exists(os.path.join(config_path, 'factory_images')):
        os.makedirs(os.path.join(config_path, 'factory_images'), exist_ok=True)
    if not os.path.exists(os.path.join(config_path, get_boot_images_dir())):
        os.makedirs(os.path.join(config_path, get_boot_images_dir()), exist_ok=True)
    if not os.path.exists(os.path.join(config_path, 'tmp')):
        os.makedirs(os.path.join(config_path, 'tmp'), exist_ok=True)
    if not os.path.exists(os.path.join(config_path, 'puml')):
        os.makedirs(os.path.join(config_path, 'puml'), exist_ok=True)


# ============================================================================
#                               Function init_db
# ============================================================================
def init_db():
    global db
    config_path = get_sys_config_path()
    # connect / create db
    db = sl.connect(os.path.join(config_path, get_pf_db()))
    db.execute("PRAGMA foreign_keys = ON")
    # create tables
    with db:
        # there could be more than one package that has the same boot.img
        # PACKAGE Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS PACKAGE (
                id INTEGER NOT NULL PRIMARY KEY,
                boot_hash TEXT NOT NULL,
                type TEXT CHECK (type IN ('firmware', 'rom')) NOT NULL,
                package_sig TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                epoch INTEGER NOT NULL
            );
        """)
        # BOOT Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS BOOT (
                id INTEGER NOT NULL PRIMARY KEY,
                boot_hash TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                is_patched INTEGER CHECK (is_patched IN (0, 1)),
                magisk_version TEXT,
                hardware TEXT,
                epoch INTEGER NOT NULL
            );
        """)
        # PACKAGE_BOOT Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS PACKAGE_BOOT (
                package_id INTEGER,
                boot_id INTEGER,
                epoch INTEGER NOT NULL,
                PRIMARY KEY (package_id, boot_id),
                FOREIGN KEY (package_id) REFERENCES PACKAGE(id),
                FOREIGN KEY (boot_id) REFERENCES BOOT(id)
            );
        """)


# ============================================================================
#                               Function get_config_file_path
# ============================================================================
def get_config_file_path():
    return os.path.join(get_sys_config_path(), CONFIG_FILE_NAME).strip()


# ============================================================================
#                               Function get_sys_config_path
# ============================================================================
def get_sys_config_path():
    return user_data_dir(APPNAME, appauthor=False, roaming=True)


# ============================================================================
#                               Function get_config_path
# ============================================================================
def get_config_path():
    global config_path
    return config_path


# ============================================================================
#                               Function set_config_path
# ============================================================================
def set_config_path(value):
    global config_path
    config_path = value


# ============================================================================
#                               Function get_labels_file_path
# ============================================================================
def get_labels_file_path():
    return os.path.join(get_config_path(), "labels.json").strip()


# ============================================================================
#                               Function get_path_to_7z
# ============================================================================
def get_path_to_7z():
    if sys.platform == "win32":
        path_to_7z =  os.path.join(get_bundle_dir(),'bin', '7z.exe')
    elif sys.platform == "darwin":
        path_to_7z =  os.path.join(get_bundle_dir(),'bin', '7zz')
    else:
        path_to_7z =  os.path.join(get_bundle_dir(),'bin', '7zzs')

    if not os.path.exists(path_to_7z):
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: {path_to_7z} is not found")
        return None
    return path_to_7z


# ============================================================================
#                               Function get_bundle_dir
# ============================================================================
# set by PyInstaller, see http://pyinstaller.readthedocs.io/en/v3.2/runtime-information.html
# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        # running in a bundle
        return sys._MEIPASS
    else:
        # running live
        return os.path.dirname(os.path.abspath(__file__))


# ============================================================================
#                               Function check_latest_version
# ============================================================================
def check_latest_version():
    try:
        response = requests.get('https://github.com/badabing2005/PixelFlasher/releases/latest')
        # look in history to find the 302, and get the loaction header
        location = response.history[0].headers['Location']
        # split by '/' and get the last item
        l_version = location.split('/')[-1]
        # If it starts with v, remove it
        if l_version[:1] == "v":
            version = l_version[1:]
        if version.count('.') == 2:
            version = f"{version}.0"
    except Exception:
        version = '0.0.0.0'
    return version


# ============================================================================
#                               Function grow_column
# ============================================================================
def grow_column(list, col, value = 20):
    w = list.GetColumnWidth(col)
    list.SetColumnWidth(col, w + value)


# ============================================================================
#                               Function open_folder
# ============================================================================
def open_folder(path, isFile = False):
    if not path:
        return
    if isFile:
        dir_path = os.path.dirname(path)
    else:
        dir_path = path
    if sys.platform == "darwin":
        subprocess.Popen(["open", dir_path])
    elif sys.platform == "win32":
        os.system(f"start {dir_path}")
    # linux
    elif get_file_explorer():
        subprocess.Popen([get_file_explorer(), dir_path])
    else:
        subprocess.Popen(["nautilus", dir_path])


# ============================================================================
#                               Function open_terminal
# ============================================================================
def open_terminal(path, isFile=False):
    if path:
        if isFile:
            dir_path = os.path.dirname(path)
        else:
            dir_path = path
        if sys.platform.startswith("win"):
            subprocess.Popen(["start", "cmd.exe", "/k", "cd", "/d", dir_path], shell=True)
        elif sys.platform.startswith("linux"):
            if get_linux_shell():
                subprocess.Popen([get_linux_shell(), "--working-directory", dir_path])
            else:
                subprocess.Popen(["gnome-terminal", "--working-directory", dir_path])
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", "-a", "Terminal", dir_path])


# ============================================================================
#                               Function check_archive_contains_file
# ============================================================================
def check_archive_contains_file(archive_file_path, file_to_check, nested=False, is_recursive=False):
    debug(f"Looking for {file_to_check} in file {archive_file_path} with nested: {nested}")

    file_ext = os.path.splitext(archive_file_path)[1].lower()

    if file_ext == '.zip':
        return check_zip_contains_file(archive_file_path, file_to_check, nested, is_recursive)
    elif file_ext in ['.tgz', '.gz', '.tar']:
        return check_tar_contains_file(archive_file_path, file_to_check, nested, is_recursive)
    else:
        debug("Unsupported file format.")
        return ''


# ============================================================================
#                               Function check_zip_conatins_file
# ============================================================================
def check_zip_contains_file(zip_file_path, file_to_check, nested=False, is_recursive=False):
    if not is_recursive:
        debug(f"Looking for {file_to_check} in zipfile {zip_file_path} with zip-nested: {nested}")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for name in zip_file.namelist():
            if name.endswith(f'/{file_to_check}') or name == file_to_check:
                if not is_recursive:
                    debug(f"Found: {name}")
                return name
            elif nested and name.endswith('.zip'):
                with zip_file.open(name, 'r') as nested_zip_file:
                    nested_zip_data = nested_zip_file.read()
                with io.BytesIO(nested_zip_data) as nested_zip_stream:
                    with zipfile.ZipFile(nested_zip_stream, 'r') as nested_zip:
                        nested_file_path = check_zip_contains_file(nested_zip_stream, file_to_check, nested=True, is_recursive=True)
                        if nested_file_path:
                            if not is_recursive:
                                debug(f"Found: {name}/{nested_file_path}")
                            return f'{name}/{nested_file_path}'
        debug(f"file: {file_to_check} was NOT found")
        return ''


# ============================================================================
#                               Function check_tar_contains_file
# ============================================================================
def check_tar_contains_file(tar_file_path, file_to_check, nested=False, is_recursive=False):
    if not is_recursive:
        debug(f"Looking for {file_to_check} in tarfile {tar_file_path} with tar-nested: {nested}")
    with tarfile.open(tar_file_path, 'r') as tar_file:
        for member in tar_file.getmembers():
            if member.name.endswith(f'/{file_to_check}') or member.name == file_to_check:
                if not is_recursive:
                    debug(f"Found: {member.name}")
                return member.name
            elif nested and member.name.endswith('.tar'):
                nested_tar_file_path = tar_file.extractfile(member).read()
                nested_file_path = check_tar_contains_file(nested_tar_file_path, file_to_check, nested=True, is_recursive=True)
                if nested_file_path:
                    if not is_recursive:
                        debug(f"Found: {member.name}/{nested_file_path}")
                    return f'{member.name}/{nested_file_path}'
            elif nested and member.name.endswith('.zip'):
                with tar_file.extractfile(member) as nested_zip_file:
                    nested_zip_data = nested_zip_file.read()

                # Create a temporary file to write the nested zip data
                with tempfile.NamedTemporaryFile(delete=False) as temp_zip_file:
                    temp_zip_file.write(nested_zip_data)

                nested_file_path = check_zip_contains_file(temp_zip_file.name, file_to_check, nested=True, is_recursive=True)
                if nested_file_path:
                    if not is_recursive:
                        debug(f"Found: {member.name}/{nested_file_path}")
                    return f'{member.name}/{nested_file_path}'
        debug(f"File {file_to_check} was NOT found")
        return ''


# ============================================================================
#                               Function get_ui_cooridnates
# ============================================================================
def get_ui_cooridnates(xmlfile, search):
    with open(xmlfile, "r", encoding='ISO-8859-1', errors="replace") as fin:
        data = fin.read()
    regex = re.compile(f"{search}.*?bounds\=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\".+")
    m = re.findall(regex, data)
    if m:
        debug(f"Found Bounds: {m[0][0]} {m[0][1]} {m[0][2]} {m[0][3]}")
        x = (int(m[0][0]) + int(m[0][2])) / 2
        y = (int(m[0][1]) + int(m[0][3])) / 2
        debug(f"Click Coordinates: {int(x)} {int(y)}")
        return f"{x} {y}"


# ============================================================================
#                               Function extract_sha1
# ============================================================================
def extract_sha1(binfile, length=8):
    with open(binfile, 'rb') as f:
        s = f.read()
        # Find SHA1=
        pos = s.find(b'\x53\x48\x41\x31\x3D')
        # Move to that location
        if pos != -1:
            # move to 5 characters from the found position
            f.seek(pos + 5, 0)
            # read length bytes
            byte_string = f.read(length)
            # convert byte string to hex string
            hex_string = binascii.hexlify(byte_string).decode('ascii')
            # convert hex string to ASCII string
            ascii_string = binascii.unhexlify(hex_string).decode('ascii', errors='replace')
            # replace non-decodable characters with ~
            ascii_string = ascii_string.replace('\ufffd', '~')
            # replace non-printable characters with !
            ascii_string = ''.join(['!' if ord(c) < 32 or ord(c) > 126 else c for c in ascii_string])
            return ascii_string
        else:
            return None


# ============================================================================
#                               Function compare_sha1
# ============================================================================
def compare_sha1(SHA1, Extracted_SHA1):
    if len(SHA1) != len(Extracted_SHA1):
        print("Warning!: The SHA1 values have different lengths")
        return 0
    else:
        num_match = 0
        for i, c in enumerate(SHA1):
            if c == Extracted_SHA1[i]:
                num_match += 1
        # return confidence level
        return num_match / len(SHA1)


# ============================================================================
#                               Function extract_fingerprint
# ============================================================================
def extract_fingerprint(binfile):
    with open(binfile, 'rb') as f:
        s = f.read()
        # Find fingerprint=
        pos = s.find(b'\x66\x69\x6E\x67\x65\x72\x70\x72\x69\x6E\x74')
        # Move to that location
        if pos == -1:
            return None
        # move to 12 characters from the found position
        f.seek(pos + 12, 0)
        # read 65 bytes
        byte_string = f.read(65)
        # convert byte string to hex string
        hex_string = binascii.hexlify(byte_string).decode('ascii')
        # convert hex string to ASCII string
        ascii_string = binascii.unhexlify(hex_string).decode('ascii', errors='replace')
        # replace non-decodable characters with ~
        ascii_string = ascii_string.replace('\ufffd', '~')
        # replace non-printable characters with !
        ascii_string = ''.join(['!' if ord(c) < 32 or ord(c) > 126 else c for c in ascii_string])
        return ascii_string


# ============================================================================
#                               Function debug
# ============================================================================
def debug(message):
    if get_verbose():
        print(f"debug: {message}")


# ============================================================================
#                               Function md5
# ============================================================================
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# ============================================================================
#                               Function sha1
# ============================================================================
def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


# ============================================================================
#                               Function sha256
# ============================================================================
def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


# ============================================================================
#                               Function get_code_page
# ============================================================================
def get_code_page():
    if sys.platform != "win32":
        return
    cp = get_system_codepage()
    if cp:
        print(f"Active code page: {cp}")
    else:
        theCmd = "chcp"
        res = run_shell(theCmd)
        if res.returncode == 0:
            # extract the code page portion
            try:
                debug(f"CP: {res.stdout}")
                cp = res.stdout.split(":")
                cp = cp[1].strip()
                cp = int(cp.replace('.',''))
                print(f"Active code page: {cp}")
                set_system_codepage(cp)
            except Exception:
                print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Unable to get Active code page.\n")
                print(f"{res.stderr}")
                print(f"{res.stdout}")
        else:
            print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Unable to get Active code page.\n")


# ============================================================================
#                               Function Which
# ============================================================================
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


# ============================================================================
#                               Function create_support_zip
# ============================================================================
def create_support_zip():
    print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} Creating support.zip file ...")
    config_path = get_config_path()
    tmp_dir_full = os.path.join(config_path, 'tmp')
    support_dir_full = os.path.join(config_path, 'support')
    support_zip = os.path.join(tmp_dir_full, 'support.zip')

    # if a previous support dir exist delete it allong with support.zip
    if os.path.exists(support_dir_full):
        debug("Deleting old support files ...")
        delete_all(support_dir_full)
    if os.path.exists(support_zip):
        debug("Deleting old support.zip ...")
        os.remove(support_zip)

    # create support folder if it does not exist
    if not os.path.exists(support_dir_full):
        os.makedirs(support_dir_full, exist_ok=True)

    # copy PixelFlasher.json to tmp\support folder
    to_copy = os.path.join(config_path, 'PixelFlasher.json')
    if os.path.exists(to_copy):
        debug(f"Copying {to_copy} to {support_dir_full}")
        shutil.copy(to_copy, support_dir_full, follow_symlinks=True)
    # copy PixelFlasher.db to tmp\support folder
    to_copy = os.path.join(config_path, get_pf_db())
    if os.path.exists(to_copy):
        debug(f"Copying {to_copy} to {support_dir_full}")
        shutil.copy(to_copy, support_dir_full, follow_symlinks=True)
    # copy labels.json to tmp\support folder
    to_copy = os.path.join(config_path, 'labels.json')
    if os.path.exists(to_copy):
        debug(f"Copying {to_copy} to {support_dir_full}")
        shutil.copy(to_copy, support_dir_full, follow_symlinks=True)
    # copy logs to support folder
    to_copy = os.path.join(config_path, 'logs')
    logs_dir = os.path.join(support_dir_full, 'logs')
    if os.path.exists(to_copy):
        debug(f"Copying {to_copy} to {support_dir_full}")
        shutil.copytree(to_copy, logs_dir)
    # copy puml to support folder
    to_copy = os.path.join(config_path, 'puml')
    puml_dir = os.path.join(support_dir_full, 'puml')
    if os.path.exists(to_copy):
        debug(f"Copying {to_copy} to {support_dir_full}")
        shutil.copytree(to_copy, puml_dir)

    # create directory/file listing
    if sys.platform == "win32":
        theCmd = f"dir /s /b \"{config_path}\" > \"{os.path.join(support_dir_full, 'files.txt')}\""
    else:
        theCmd = f"ls -lRgn \"{config_path}\" > \"{os.path.join(support_dir_full, 'files.txt')}\""
    debug(f"{theCmd}")
    res = run_shell(theCmd)

    # sanitize json
    file_path = os.path.join(support_dir_full, 'PixelFlasher.json')
    if os.path.exists(file_path):
        sanitize_file(file_path)
    # sanitize files.txt
    file_path = os.path.join(support_dir_full, 'files.txt')
    if os.path.exists(file_path):
        sanitize_file(file_path)

    # for each file in logs, sanitize
    for filename in os.listdir(logs_dir):
        file_path = os.path.join(logs_dir, filename)
        if os.path.exists(file_path):
            sanitize_file(file_path)

    # for each file in logs, sanitize
    for filename in os.listdir(puml_dir):
        file_path = os.path.join(puml_dir, filename)
        if os.path.exists(file_path):
            sanitize_file(file_path)

    # sanitize db
    file_path = os.path.join(support_dir_full, get_pf_db())
    if os.path.exists(file_path):
        sanitize_db(file_path)

    # zip support folder
    debug(f"Zipping {support_dir_full} ...")
    shutil.make_archive(support_dir_full, 'zip', support_dir_full)


# ============================================================================
#                               Function sanitize_file
# ============================================================================
def sanitize_file(filename):
    debug(f"Santizing {filename} ...")
    with contextlib.suppress(Exception):
        with open(filename, "rt", encoding='ISO-8859-1', errors="replace") as fin:
            data = fin.read()
        data = re.sub(r'(\\Users\\+)(?:.*?)(\\+)', r'\1REDACTED\2', data, flags=re.IGNORECASE)
        data = re.sub(r'(\/Users\/+)(?:.*?)(\/+)', r'\1REDACTED\2', data, flags=re.IGNORECASE)
        data = re.sub(r'(\"device\":\s+)(\"\w+?\")', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(device\sid:\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(device:\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(Rebooting device\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(Flashing device\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(waiting for\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(Serial\sNumber\.+\:\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(fastboot(.exe)?\"? -s\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(adb(.exe)?\"? -s\s+)(\w+)', r'\1REDACTED', data, flags=re.IGNORECASE)
        data = re.sub(r'(\S\  \((?:adb|f\.b|rec|sid)\)   )(.+?)(\s+.*)', r'\1REDACTED\3', data, flags=re.IGNORECASE)
        with open(filename, "wt", encoding='ISO-8859-1', errors="replace") as fin:
            fin.write(data)


# ============================================================================
#                               Function sanitize_db
# ============================================================================
def sanitize_db(filename):
    debug(f"Santizing {filename} ...")
    con = sl.connect(filename)
    cursor = con.cursor()
    with con:
        data = con.execute("SELECT id, file_path FROM BOOT")
        for row in data:
            id = row[0]
            file_path = row[1]
            if sys.platform == "win32":
                file_path_sanitized = re.sub(r'(\\Users\\+)(?:.*?)(\\+)', r'\1REDACTED\2', file_path, flags=re.IGNORECASE)
            else:
                file_path_sanitized = re.sub(r'(\/Users\/+)(?:.*?)(\/+)', r'\1REDACTED\2', file_path, flags=re.IGNORECASE)
            cursor.execute(f"Update BOOT set file_path = '{file_path_sanitized}' where id = {id}")
            con.commit()
    with con:
        data = con.execute("SELECT id, file_path FROM PACKAGE")
        for row in data:
            id = row[0]
            file_path = row[1]
            if sys.platform == "win32":
                file_path_sanitized = re.sub(r'(\\Users\\+)(?:.*?)(\\+)', r'\1REDACTED\2', file_path, flags=re.IGNORECASE)
            else:
                file_path_sanitized = re.sub(r'(\/Users\/+)(?:.*?)(\/+)', r'\1REDACTED\2', file_path, flags=re.IGNORECASE)
            cursor.execute(f"Update PACKAGE set file_path = '{file_path_sanitized}' where id = {id}")
            con.commit()


# ============================================================================
#                               Function purge
# ============================================================================
# This function delete multiple files matching a pattern
def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


# ============================================================================
#                               Function delete_all
# ============================================================================
# This function delete multiple files matching a pattern
def delete_all(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


# ============================================================================
#                               Function run_shell
# ============================================================================
# We use this when we want to capture the returncode and also selectively
# output what we want to console. Nothing is sent to console, both stdout and
# stderr are only available when the call is completed.
def run_shell(cmd, timeout=None):
    try:
        response = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='ISO-8859-1', errors="replace", timeout=timeout)
        wx.Yield()
        return response
    except subprocess.TimeoutExpired as e:
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Command timed out after {timeout} seconds")
        puml("#red:Command timed out;\n", True)
        puml(f"note right\n{e}\nend note\n")
    except Exception as e:
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Encountered an error while executing run_shell")
        print(e)
        puml("#red:Encountered an error;\n", True)
        puml(f"note right\n{e}\nend note\n")
        raise e


# ============================================================================
#                               Function run_shell2
# ============================================================================
# This one pipes the stdout and stderr to Console text widget in realtime,
# no returncode is available.
def run_shell2(cmd, timeout=None):
    try:
        class obj(object):
            pass

        response = obj()
        proc = subprocess.Popen(f"{cmd}", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='ISO-8859-1', errors="replace")

        print
        stdout = ''
        start_time = time.time()
        while True:
            line = proc.stdout.readline()
            wx.Yield()
            if line.strip() != "":
                print(line.strip())
                stdout += line
            if not line:
                break
            if timeout is not None and time.time() > timeout:
                proc.terminate()
                print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Command timed out after {timeout} seconds")
                puml("#red:Command timed out;\n", True)
                puml(f"note right\nCommand timed out after {timeout} seconds\nend note\n")
                return None
        proc.wait()
        response.stdout = stdout
        return response
    except Exception as e:
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S} ERROR: Encountered an error while executing run_shell2")
        print(e)
        puml("#red:Encountered an error;\n", True)
        puml(f"note right\n{e}\nend note\n")
        raise e


