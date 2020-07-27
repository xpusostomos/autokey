# Copyright (C) 2011 Chris Dekter
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

class MatchWindow:
    def __init__(self):
        self.match = False
        self.window_info = None

    def get_active_title(self):
        """
        Get the visible title of the currently active window

        Usage: C{window.get_active_title()}

        @return: the visible title of the currentle active window
        @rtype: C{str}
        """
        return self.window_info.wm_title

    def get_active_class(self):
        """
        Get the class of the currently active window

        Usage: C{window.get_active_class()}

        @return: the class of the currentle active window
        @rtype: C{str}
        """
        return self.window_info.wm_class

    @property
    def active_title(self):
        return self.window_info.wm_title

    @property
    def active_class(self):
        return self.window_info.wm_class
