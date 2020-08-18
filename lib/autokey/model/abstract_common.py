# Copyright (C) 2011 Chris Dekter
# Copyright (C) 2019-2020 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import typing
import os

from autokey.model.helpers import TriggerMode, JSON_FILE_PATTERN, MATCH_FILE_PATTERN
from autokey.script_runner import SimpleScript


class AbstractCommon:
    def __init__(self, path):
        self.path = path
        self.enabled = True
        self.show_in_tray_menu = False
        self.enabled = True
        self.parent = None
        self.usageCount = 0
        self.modes = []  # type: typing.List[TriggerMode]
        self.match_script = SimpleScript('', '')

    def load_from_serialized(self, data):
        self.data = data
        self.usageCount = data.get("usageCount")
        self.modes = [TriggerMode(item) for item in data["modes"]]
        self.enabled = data.get("enabled")
        self.show_in_tray_menu = data.get("showInTrayMenu")

    def copy_common(self, item):
        self.match_script = SimpleScript(item.match_script.path, item.match_script.code)
        self.parent = item.parent
        self.show_in_tray_menu = item.show_in_tray_menu
        self.enabled = item.enabled

    @property
    def json_path(self):
        if os.path.isdir(self.path):
            directory = self.path
            base_name = "folder"
        else:
            directory, filename = os.path.split(self.path)
            base_name, ext = os.path.splitext(filename)
        return JSON_FILE_PATTERN.format(directory, base_name)

    @property
    def match_path(self):
        if os.path.isdir(self.path):
            directory = self.path
            base_name = "folder"
        else:
            directory, filename = os.path.split(self.path)
            base_name, ext = os.path.splitext(filename)
        return MATCH_FILE_PATTERN.format(directory, base_name)
