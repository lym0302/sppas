#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of TierMapping.
#
# TierMapping is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TierMapping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TierMapping.  If not, see <http://www.gnu.org/licenses/>.

import wx

from views.TierMappingFrame import TierMappingFrame
from presenters.TierMappingPresenter import TierMappingPresenter


class TierMappingApp(wx.App):
    def __init__(self, files=None, mapchar=None):
        wx.App.__init__(self, False)
        view = TierMappingFrame(parent=None)
        presenter = TierMappingPresenter(view, files, mapchar)
        self.SetTopWindow(view)
