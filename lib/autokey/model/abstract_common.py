import os

from lib.autokey.model.helpers import TriggerMode, JSON_FILE_PATTERN, MATCH_FILE_PATTERN
from lib.autokey.script_runner import SimpleScript


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
        self.match_script = SimpleScript(source_phrase.match_script.path, source_phrase.match_script.code)
        self.parent = source_phrase.parent
        self.show_in_tray_menu = source_phrase.show_in_tray_menu
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
