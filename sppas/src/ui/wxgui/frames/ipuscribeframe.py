# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.wxgui.frames.ipuscribeframe.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI manual orthographic transcription for SPPAS.

"""
import wx

from sppas.src.ui.wxgui.clients.ipuscribeclient import IPUscribeClient
from sppas.src.ui.wxgui.sp_icons import IPUSCRIBE_APP_ICON
from sppas.src.ui.wxgui.sp_icons import SAVE_FILE
from sppas.src.ui.wxgui.sp_icons import SAVE_ALL_FILE

from .baseframe import ComponentFrame

# ----------------------------------------------------------------------------

SAVE_ALL_ID = wx.NewId()

# ----------------------------------------------------------------------------


class IPUscribeFrame(ComponentFrame):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      IPUscribe allows to transcribe manually speech files inside IPUs.

    """
    def __init__(self, parent, idc, prefsIO):

        arguments = {}
        arguments['files'] = []
        arguments['title'] = "SPPAS - IPUscriber"
        arguments['type']  = "SOUNDFILES"
        arguments['icon']  = IPUSCRIBE_APP_ICON
        arguments['prefs'] = prefsIO

        ComponentFrame.__init__(self, parent, idc, arguments)
        self._add_accelerator()

        self.toolbar.AddButton(wx.ID_SAVE, SAVE_FILE, "Save")
        self.toolbar.AddButton(SAVE_ALL_ID, SAVE_ALL_FILE, "Save all")
        self.Bind(wx.EVT_BUTTON, self.IPUscribeProcessEvent)

        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def _add_accelerator(self):
        """ Set the accelerator table. """

        # Save with CTRL+S
        accelS = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE)

        # Save all with CTRL+SHIFT+S
        accelSS = wx.AcceleratorEntry(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), SAVE_ALL_ID)
        
        # Quit with ATL+F4
        accelQ = wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([ accelQ, accelS, accelSS ])
        self.SetAcceleratorTable(accel_tbl)

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """ Override. """

        return IPUscribeClient(parent,prefsIO)

    # ------------------------------------------------------------------------

    def IPUscribeProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        ide = event.GetId()

        if ide == wx.ID_SAVE:
            self._clientpanel.Save()
            return True

        elif ide == SAVE_ALL_ID:
            self._clientpanel.SaveAll()
            return True

        else:
            ComponentFrame.ProcessEvent(self, event)
            
# ----------------------------------------------------------------------------