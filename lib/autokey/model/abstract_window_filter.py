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

import re

INHERITED_FROM_PARENT = '{ inherited from parent } '
NONE_CONFIGURED = '{ none configured }'

class AbstractWindowFilter:

    def __init__(self):
        self.windowInfoRegex = None
        self.isRecursive = False

    def get_serializable(self):
        if self.windowInfoRegex is not None:
            return {"regex": self.windowInfoRegex.pattern, "isRecursive": self.isRecursive}
        else:
            return {"regex": None, "isRecursive": False}

    def load_from_serialized(self, data):
        try:
            if isinstance(data, dict): # check needed for data from versions < 0.80.4
                self.set_window_titles(data["regex"])
                self.isRecursive = data["isRecursive"]
            else:
                self.set_window_titles(data)
        except re.error as e:
            raise e

    def copy_window_filter(self, window_filter):
        self.windowInfoRegex = window_filter.windowInfoRegex
        self.isRecursive = window_filter.isRecursive

    def set_window_titles(self, regex):
        if regex is not None:
            try:
                self.windowInfoRegex = re.compile(regex, re.UNICODE)
            except re.error as e:
                raise e
        else:
            self.windowInfoRegex = None

    def set_filter_recursive(self, recurse):
        self.isRecursive = recurse

    # TODO CJB probably obsolete
    def has_filter(self) -> bool:
        return self.windowInfoRegex is not None

    # TODO CJB probably obsolete
    def inherits_filter(self) -> bool:
        if self.parent is not None:
            return self.parent.has_applicable_filter()

        return False

    # TODO CJB obsolete
    def get_child_filter(self):
        if self.isRecursive and self.windowInfoRegex is not None:
            return self.get_filter_regex()
        elif self.parent is not None:
            return self.parent.get_child_filter()
        else:
            return ""

    # TODO CJB obsolete
    def get_filter_regex(self):
        """
        Used by the GUI to obtain human-readable version of the filter
        """
        if self.windowInfoRegex is not None:
            if self.isRecursive:
                return self.windowInfoRegex.pattern
            else:
                return self.windowInfoRegex.pattern
        elif self.parent is not None:
            return self.parent.get_child_filter()
        else:
            return ""

    # TODO CJB probably obsolete
    def filter_matches(self, otherFilter):
        # XXX Should this be and?
        if otherFilter is None or not self.has_applicable_filter():
            return True
        return otherFilter == self.get_applicable_filter().windowInfoRegex.pattern

    def get_filter_display_text(self):
        item = self.get_applicable_filter()
        rtn = ''
        if (item != self):
            rtn += INHERITED_FROM_PARENT
        if item is not None:
            pattern = ''
            if item.windowInfoRegex is not None:
                pattern = item.windowInfoRegex.pattern
            rtn += AbstractWindowFilter.get_filter_display_text_from(pattern, item.match_code)
        else:
            rtn = NONE_CONFIGURED
        return rtn

    @staticmethod
    def get_filter_display_text_from(pattern, match_code):
        rtn = ''
        rtn += pattern
        rtn += match_code.replace('\n', ' ... ')
        if rtn == '':
            rtn = NONE_CONFIGURED
        return rtn

    def same_filter_as_item(self, otherItem):
        if not isinstance(otherItem, AbstractWindowFilter):
            return False
        return self.filter_matches(otherItem.get_applicable_filter())

    def get_applicable_filter(self, forChild=False):
        if self.windowInfoRegex is not None or self.match_code != '':
            if (forChild and self.isRecursive) or not forChild:
                return self
        elif self.parent is not None:
            return self.parent.get_applicable_filter(True)

        return None

    def has_applicable_filter(self):
        return self.get_applicable_filter(False) is not None

    def _should_trigger_window_title(self, window_info):
        r = self.get_applicable_filter()  # type: typing.Pattern
        if r is not None and r.windowInfoRegex is not None:
            return bool(r.windowInfoRegex.match(window_info.wm_title)) or bool(r.windowInfoRegex.match(window_info.wm_class))
        else:
            return False
