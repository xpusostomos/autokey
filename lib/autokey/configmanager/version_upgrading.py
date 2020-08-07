# Copyright (C) 2011 Chris Dekter
# Copyright (C) 2018 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Sometimes, changes in code require updating the format of existing user data.
This module handles upgrading user data, if required.
The stored user data contains a version field with the autokey version that created it. This is used to determine
if any patches must be applied.

Each converter function altering the configuration data MUST NOT change the "version" item in the configuration data to
a different version (so NEVER set to common.VERSION), because this might skip additional conversion steps.

Example: Let the current version be 0.97.0. If 0.96.1 introduces a conversion step, and old 0.70.x data is found,
setting config_data["version"] to common.VERSION ("0.97.0") inside the conversion function convert_v0_70_to_v0_80 will
skip the required conversion task for 0.96.1.

Additionally, it will skip further conversion tasks that require the model to be present, which are executed in the
ConfigManager later. The ConfigManager is responsible for updating the data version.

Do not require the user to install all versions one after another in order to get all data patches. Such skips might
happen with LTS distribution releases that skip several autokey versions during their lifetime.
"""

import os
from pathlib import Path

import autokey.model.folder
import autokey.model.phrase
import autokey.model.script
from autokey import common
import autokey.configmanager.configmanager_constants as cm_constants
import glob

from lib.autokey.model.abstract_window_filter import AbstractWindowFilter
from lib.autokey.model.folder import Folder

logger = __import__("autokey.logger").logger.get_logger(__name__)


def upgrade_configuration(configuration_manager, config_data: dict):
    """Updates the global configuration data to the latest version."""
    version = config_data["version"]
    if version < "0.80.0":
        convert_v0_70_to_v0_80(config_data, version)
        configuration_manager.config_altered(True)
    if version < "0.95.3":
        convert_autostart_entries_for_v0_95_3()
    if version < "0.95.12":
        convertDotFiles_v95_11(config_data)
    if version < "0.95.12":
        convert_script_filter_for_v0_95_11(config_data, version)
    # Put additional conversion steps here.


def convert_v0_70_to_v0_80(config_data, old_version: str):
    try:
        _convert_v0_70_to_v0_80(config_data, old_version)
    except Exception:
        logger.exception(
            "Problem occurred during conversion. "
            "Existing config file has been saved as {}{}".format(cm_constants.CONFIG_FILE, old_version)
        )
        raise


def _convert_v0_70_to_v0_80(config_data, old_version: str):
    os.rename(cm_constants.CONFIG_FILE, cm_constants.CONFIG_FILE + old_version)
    logger.info("Converting v{} configuration data to v0.80.0".format(old_version))
    for folder_data in config_data["folders"]:
        _convert_v0_70_to_v0_80_folder(folder_data, None)

    config_data["folders"] = []
    config_data["settings"][cm_constants.NOTIFICATION_ICON] = common.ICON_FILE_NOTIFICATION

    # Remove old backup file so we never retry the conversion
    if os.path.exists(cm_constants.CONFIG_FILE_BACKUP):
        os.remove(cm_constants.CONFIG_FILE_BACKUP)

    logger.info("Conversion succeeded")


def _convert_v0_70_to_v0_80_folder(folder_data, parent):
    f = autokey.model.folder.Folder("")
    f.inject_json_data(folder_data)
    f.parent = parent
    f.persist()

    for subfolder in folder_data["folders"]:
        _convert_v0_70_to_v0_80_folder(subfolder, f)

    for itemData in folder_data["items"]:
        i = None
        if itemData["type"] == "script":
            i = autokey.model.script.Script("", "", "")
            i.code = itemData["code"]
        elif itemData["type"] == "phrase":
            i = autokey.model.phrase.Phrase("", "")
            i.phrase = itemData["phrase"]

        if i is not None:
            i.inject_json_data(itemData)
            i.parent = f
            i.persist()


def convert_autostart_entries_for_v0_95_3():
    """
    In versions <= 0.95.2, the autostart option in autokey-gtk copied the default autokey-gtk.desktop file into
    $XDG_CONFIG_DIR/autostart (with minor, unrelated modifications).
    For versions >= 0.95.3, the autostart file is renamed to autokey.desktop. In 0.95.3, the autostart functionality
    is implemented for autokey-qt. Thus, it becomes possible to have an autostart file for both GUIs in the autostart
    directory simultaneously. Because of the singleton nature of autokey, this becomes an issue and race-conditions
    determine which GUI starts first. To prevent this, both GUIs will share a single autokey.desktop autostart entry,
    allowing only one GUI to be started during login. This allows for much simpler code.
    """
    old_autostart_file = Path(common.AUTOSTART_DIR) / "autokey-gtk.desktop"
    if old_autostart_file.exists():
        new_file_name = Path(common.AUTOSTART_DIR) / "autokey.desktop"
        logger.info("Found old autostart entry: '{}'. Rename to: '{}'".format(
            old_autostart_file, new_file_name)
        )
        old_autostart_file.rename(new_file_name)

def convertDotFiles_v95_11(config_data):
    folders = [*config_data["folders"], *glob.glob(cm_constants.CONFIG_DEFAULT_FOLDER + "/*")]
    for name in folders:
        convertDotFiles_v95_11_folder(Path(name))

def convertDotFiles_v95_11_folder(p: Path):
    for name in p.glob('.*.json'):
        new_json = p / name.name[1:]
        name.rename(new_json)

    for name in p.iterdir():
        if name.is_dir():
            convertDotFiles_v95_11_folder(name)

def convert_script_filter_for_v0_95_11(config_data, old_version: str):
    folders = [*config_data["folders"], *glob.glob(cm_constants.CONFIG_DEFAULT_FOLDER + "/*")]
    for folder_data in folders:
        if os.path.isdir(folder_data):
            f = autokey.model.folder.Folder("", path=folder_data)
            f.load(None)
            _convert_script_filter_for_v0_95_11_folder(f)

def _convert_script_filter_for_v0_95_11_folder(f: Folder):
    # f = autokey.model.folder.Folder("", path=folder_data)
    # f.load(parent)
    f.match_script.code = _convert_regex_to_code_for_v0_95_11(f)
    f.persist()

    for subfolder in f.folders:
        _convert_script_filter_for_v0_95_11_folder(subfolder)

    for i in f.items:
        i.load(f)
        i.match_script.code = _convert_regex_to_code_for_v0_95_11(i)
        i.persist()

def _convert_regex_to_code_for_v0_95_11(item: AbstractWindowFilter):
    script = ''
    if "filter" in item.data:
        filter = item.data["filter"]
        if "regex" in filter:
            regex = filter["regex"]
            if regex is not None:
                script += 'if re.match("' + regex + '", window.active_class):\n    window.match = True\n'
                script += 'if re.match("' + regex + '", window.active_title):\n    window.match = True\n'
    return script


