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

from lib.autokey.script_runner import ScriptRunner



class AbstractWindowFilter:

    INHERITED_FROM_PARENT = '{ inherited from parent } '
    NONE_CONFIGURED = '{ none configured }'

    def __init__(self):
        # self.windowInfoRegex = None
        self.isRecursive = False

    def get_serializable(self):
        # if self.windowInfoRegex is not None:
        #     return {"regex": self.windowInfoRegex.pattern, "isRecursive": self.isRecursive}
        # else:
        # return {"regex": None, "isRecursive": False}
        return {"isRecursive": False}

    def load_from_serialized(self, data):
        try:
            if isinstance(data, dict): # check needed for data from versions < 0.80.4
                # self.set_window_titles(data["regex"])
                self.isRecursive = data["isRecursive"]
            # else:
            #     self.set_window_titles(data)
        except re.error as e:
            raise e

    def copy_window_filter(self, window_filter):
        # self.windowInfoRegex = window_filter.windowInfoRegex
        self.isRecursive = window_filter.isRecursive

# TODO CJB what did this used to do?
    # def set_window_titles(self, regex):
    #     if regex is not None:
    #         try:
    #             self.windowInfoRegex = re.compile(regex, re.UNICODE)
    #         except re.error as e:
    #             raise e
    #     else:
    #         self.windowInfoRegex = None

    def set_filter_recursive(self, recurse):
        self.isRecursive = recurse

    # TODO CJB probably obsolete
    def has_filter(self) -> bool:
        return self.match_script.code != ''
        # return self.windowInfoRegex is not None and self.match_code != ''

    # TODO CJB probably obsolete
    def inherits_filter(self) -> bool:
        if self.parent is not None:
            return self.parent.has_applicable_filter()

        return False

    # TODO CJB obsolete
    # def get_child_filter(self):
    #     if self.isRecursive and self.windowInfoRegex is not None:
    #         return self.get_filter_regex()
    #     elif self.parent is not None:
    #         return self.parent.get_child_filter()
    #     else:
    #         return ""

    # # TODO CJB obsolete
    # def get_filter_regex(self):
    #     """
    #     Used by the GUI to obtain human-readable version of the filter
    #     """
    #     if self.windowInfoRegex is not None:
    #         if self.isRecursive:
    #             return self.windowInfoRegex.pattern
    #         else:
    #             return self.windowInfoRegex.pattern
    #     elif self.parent is not None:
    #         return self.parent.get_child_filter()
    #     else:
    #         return ""

    # # TODO CJB probably obsolete
    # def filter_matches(self, otherFilter):
    #     # XXX Should this be and?
    #     if otherFilter is None or not self.has_applicable_filter():
    #         return True
    #     return otherFilter == self.get_applicable_filter().windowInfoRegex.pattern

    def get_filter_display_text(self):
        item = self.get_applicable_filter()
        rtn = ''
        if (item != self):
            rtn += AbstractWindowFilter.INHERITED_FROM_PARENT
        if item is not None:
            # pattern = ''
            # if item.windowInfoRegex is not None:
            #     pattern = item.windowInfoRegex.pattern
            rtn += AbstractWindowFilter.get_filter_display_text_from(item.match_script.code)
        else:
            rtn = AbstractWindowFilter.NONE_CONFIGURED
        if len(rtn) > 80:
            rtn = rtn[:80] + '...'
        return rtn

    @staticmethod
    def get_filter_display_text_from(match_code):
        rtn = ''
        # rtn += pattern
        rtn += match_code.replace('\n', ' ')
        if rtn == '':
            rtn = AbstractWindowFilter.NONE_CONFIGURED
        return rtn

    # def same_filter_as_item(self, otherItem):
    #     if not isinstance(otherItem, AbstractWindowFilter):
    #         return False
    #     return self.filter_matches(otherItem.get_applicable_filter())

    def get_applicable_filter(self, forChild=False):
        # if self.windowInfoRegex is not None or self.match_code != '':
        if self.match_script.code != '':
            if (forChild and self.isRecursive) or not forChild:
                return self
        elif self.parent is not None:
            return self.parent.get_applicable_filter(True)
        return None

    def has_applicable_filter(self):
        # print("has applicable filter: " + str(self.get_applicable_filter(False) is not None))
        return self.get_applicable_filter(False) is not None

    # def _should_trigger_window_title(self, window_info):
    #     r = self.get_applicable_filter()  # type: typing.Pattern
    #     if r is not None:
    #         return bool(r.windowInfoRegex.match(window_info.wm_title)) or bool(r.windowInfoRegex.match(window_info.wm_class))
    #     else:
    #         return True

    def _should_trigger_window_title(self, window_info, script_runner: ScriptRunner):
        # print("should_trigger_window_title: " + str(window_info) + " " + self.path)
        filter_item = self.get_applicable_filter()
        if filter_item is None:
            return True
        # elif item.windowInfoRegex is not None:
        #     return item._should_trigger_window_title(window_info)
        else:
            filter_item = self.get_applicable_filter()
            scope = script_runner.scope.copy()
            scope["window"].window_info = window_info
            scope["window"].match = False
            # print("run match: " + str(self) + ' path: ' + filter_item.match_path + " item: " + self.path)
            # script_runner.execute_match(filter_item, scope)
            script_runner.execute_script(filter_item.match_script)
            # if scope["window"].match:
            print("should_trigger_window_title: " + str(window_info) + " " + str(scope["window"].match))
            return scope["window"].match
