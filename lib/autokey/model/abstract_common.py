from lib.autokey.model.helpers import TriggerMode, JSON_FILE_PATTERN, MATCH_FILE_PATTERN


class AbstractCommon:
    def __init__(self, path):
        self.path = path
        self.enabled = True
        self.show_in_tray_menu = False
        self.enabled = True
        self.parent = None
        self.usageCount = 0
        self.modes = []  # type: typing.List[TriggerMode]

    def load_from_serialized(self, data):
        self.data = data
        self.usageCount = data["usageCount"]
        self.modes = [TriggerMode(item) for item in data["modes"]]
        self.enabled = data["enabled"]
        self.show_in_tray_menu = data["showInTrayMenu"]

    def copy_common(self, item):
        self.enabled = item.enabled

    @property
    def json_path(self):
        directory, base_name = os.path.split(self.path[:-3])
        return JSON_FILE_PATTERN.format(directory, base_name)

    @property
    def match_path(self):
        directory, base_name = os.path.split(self.path[:-3])
        return MATCH_FILE_PATTERN.format(directory, base_name)
