#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015-2016  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ----------------------------------------------------------------------------
# File: annotationctrl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import logging

import wx
import wx.lib.newevent

from wxgui.cutils.colorutils import PickRandomColour, ContrastiveColour
from wxgui.cutils.textutils  import TextAsNumericValidator

from pointctrl import PointCtrl
from pointctrl import spEVT_MOVING,spEVT_MOVED,spEVT_RESIZING,spEVT_RESIZED, spEVT_POINT_LEFT
from pointctrl import MIN_W as pointctrlMinWidth

from labelctrl import LabelCtrl
from labelctrl import spEVT_LABEL_LEFT

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

MIN_W=2
MIN_H=8

NORMAL_COLOUR    = wx.Colour(0,0,0)
UNCERTAIN_COLOUR = wx.Colour(70,70,180)

STYLE=wx.NO_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE

FONT_SIZE_MIN = 8
FONT_SIZE_MAX = 32

PANE_WIDTH_MIN = 10
PANE_WIDTH_MAX = 200
PANE_WIDTH     = 100

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Class PaneTierCtrl
# ----------------------------------------------------------------------------

class AnnotationCtrl( wx.Window ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display an annotation (see annotationdata).

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 ann=None):
        """
        Constructor.

        Non-wxpython related parameters:

        @param ann (Annotation) the annotation to be represented.

        The size is representing the available area to draw the annotation.
        The member _pxsec must be fixed for the annotation to draw inside this
        area. It represents the number of pixels required for 1 second.

        """
        self._pointctrl1 = None
        self._pointctrl2 = None
        self._labelctrl  = None
        self._pxsec      = 0  # the number of pixels to represent 1 second of time

        wx.Window.__init__( self, parent, id, pos, size, STYLE )
        self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
        self.SetDoubleBuffered( True )

        # Members, Initializations
        self._ann = None
        if ann is not None:
            self.SetAnn(ann)
        self.Reset( size )

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)

    #------------------------------------------------------------------------

    def Reset(self, size=None):
        """
        Reset all members to their default.

        @param size (wx.Size)

        """
        self._selected = False
        self.__initializeColours()
        if size:
            self.__initialSize(size)

    #------------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Look & style
    #------------------------------------------------------------------------

    def SetLabelFont(self, font):
        """
        Override. Set a new font.

        """

        if self._labelctrl: self._labelctrl.SetFont( self.GetFont() )

    #------------------------------------------------------------------------

    def SetLabelAlign(self, value):
        """
        Fix the position of the text of an annotation.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if self._labelctrl: self._labelctrl.SetAlign( value )

    #------------------------------------------------------------------------

    def SetLabelColours(self, bgcolour=None, fontnormalcolour=None, fontuncertaincolour=None):
        """
        Change the main colors of the Label.
        Notice that uncertain labels can be of a different color,
        like links in web browsers.

        @param bgcolour (wx.Colour)
        @param fontcolour (wx.Colour)
        @param fontuncertaincolour (wx.Colour)

        """
        if self._labelctrl is None: return
        if self._labelctrl.GetValue().GetSize() == 1:
            self._labelctrl.SetColours(bgcolour,fontnormalcolour)
        else:
            self._labelctrl.SetColours(bgcolour,fontuncertaincolour)

    #------------------------------------------------------------------------

    def SetBorderColour(self, colour):
        """
        Fix the color of the top/bottom lines.

        """
        self._penbordercolor = wx.Pen(colour,1,wx.SOLID)

    #------------------------------------------------------------------------

    def GetHeight(self):
        """
        Return the current height.

        """
        return self.GetSize().height

    # -----------------------------------------------------------------------

    def GetAnn(self):
        """
        Return the annotation to draw.

        """
        return self._ann

    # -----------------------------------------------------------------------

    def SetAnn(self, ann):
        """
        Set the annotation.

        @param ann (annotation)

        """
        try:
            self._pointctrl1 = PointCtrl(self, id=-1, point=ann.GetLocation().GetBegin())
            self._pointctrl2 = PointCtrl(self, id=-1, point=ann.GetLocation().GetEnd())
        except Exception:
            self._pointctrl1 = PointCtrl(self, id=-1, point=ann.GetLocation().GetPoint())
            self._pointctrl1 = None
        self._labelctrl  = LabelCtrl(self, id=-1, label=ann.GetLabel())
        self._ann = ann

    #------------------------------------------------------------------------

    def SetPxSec(self, value):
        if value<0:
            raise ValueError
        self._pxsec = int(value)
        self.Refresh()

    #------------------------------------------------------------------------
    # Methods to move/resize objects
    #------------------------------------------------------------------------

    def SetHeight(self, height):
        """
        Set the height (int).

        @param height (int) in pixels

        """
        if self._pointctrl1: self._pointctrl1.SetHeight( height )
        if self._pointctrl2: self._pointctrl2.SetHeight( height )
        if self._labelctrl:  self._labelctrl.SetHeight( height )

    #------------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """
        Define a new position and/or size to display.

        @param pos (wx.Point)
        @param size (wx.Size)

        """
        (w,h) = size
        (x,y) = pos
        (ow,oh) = self.GetSize()
        (ox,oy) = self.GetPosition()

        # New width
        if ow != w:
            self.SetSize( wx.Size(w,oh) )

        # New height
        if oh != h:
            self.SetHeight(h)

        # New position (x and/or y)
        if ox != x or oy != y:
            self.Move(pos)



    #------------------------------------------------------------------------


    #------------------------------------------------------------------------
    # Callbacks
    #------------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """
        Handles the wx.EVT_MOUSE_EVENTS event for PaneTierCtrl.

        """

        if event.Entering():
            if self._selected is False:
                self._selected = True
                self.Refresh()

        elif event.Leaving():
            self._selected = False
            self.Refresh()

        wx.PostEvent(self.GetParent(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Painting
    #------------------------------------------------------------------------

    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for PointCtrl.

        """
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    #------------------------------------------------------------------------

    def Draw(self, dc):
        """
        Draw the PointCtrl on the DC.

        @param dc (wx.DC) The device context to draw on.

        """
        logging.debug('Draw...')

        # Get the actual client size of ourselves
        # Notice that the size is corresponding to the available size on screen
        # for that annotation. It can often happen that the annotation-duration
        # is larger than the available width.
        w,h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if w*h==0: return

        # Initialize the DC
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.Clear()

        # Content
        self.DrawContent(dc, w,h)

        if self._selected:
            self.DrawBorder(dc, w,h)

    #------------------------------------------------------------------------

    def DrawContent(self, dc, w,h):
        """
        Draw the annotation on the DC.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        if self._ann is None: return

        h = h-4

        logging.debug('  Draw content for ann %s: w=%d, h=%d'%(self._ann,w,h))
        y=2

        wpt1 = max(pointctrlMinWidth,self._calcW(self._pointctrl1.GetValue().Duration().GetValue()))
        if wpt1>w: wpt1=w

        logging.debug('  ... Draw content: wpt1=%d'%wpt1)

        if self._pointctrl2 is None:
            tw = min(50, self.__getTextWidth(self._labelctrl.GetValue().GetValue())+2 )
            if (wpt1+tw) > w: # ensure to stay in our allocated area
                tw = w - wpt1 # reduce width to the available area
            tw = max(0,tw)
            logging.debug('  ... Draw content: tw=%d'%wpt1)
            self._labelctrl.MoveWindow(wx.Point(wpt1,y), wx.Size(tw,h))
        else:
            xtime1 = self._pointctrl1.GetValue().GetMidpoint() - self._pointctrl1.GetValue().GetRadius()
            xtime2 = self._pointctrl2.GetValue().GetMidpoint() + self._pointctrl2.GetValue().GetRadius()
            wpt2 = max(pointctrlMinWidth, self._calcW(self._pointctrl2.GetValue().Duration().GetValue()))
            xpt2 = self._calcW(xtime2-xtime1) - wpt2
            tx = wpt1
            tw = xpt2-wpt1
            if (tx+tw) > w:           # ensure to stay in our allocated area
                tw = tw - ((tx+tw)-w) # reduce width to the available area
            tw = max(0,tw)
            logging.debug('  ... Draw label: tw=%d, xpt2=%d'%(tw,xpt2))
            self._labelctrl.MoveWindow(wx.Point(tx,y), wx.Size(tw,h))
        self._labelctrl.Show()

        # Draw the points
        self._drawPoint(self._pointctrl1, 0,y, w,h)
        if self._pointctrl2 is not None:
            self._drawPoint(self._pointctrl2, xpt2,y, wpt2,h)

    #------------------------------------------------------------------------

    def DrawBorder(self, dc, w,h):
        """
        """
        x=0
        y=0
        logging.debug('  Draw border: x=%d,y=%d,w=%d,h=%d'%(x,y,w,h))
        # Top and Bottom lines
        dc.SetPen( self._penbordercolor )
        dc.DrawLine(x,y,  x+w,y)       # horizontal, top
        dc.DrawLine(x,h-2,x+w,h-2)     # horizontal, bottom
        dc.DrawLine(x,y,  x,y+h)       # vertical, left
        dc.DrawLine(x+w-2,y,x+w-2,y+h) # vertical, right

        dc.SetBrush(wx.Brush(wx.RED, wx.BDIAGONAL_HATCH))
        dc.DrawRectangle(x, y, w, h)

    #------------------------------------------------------------------------
    # Private
    #------------------------------------------------------------------------

    def _drawPoint(self, point, x,y, w,h):
        """ Display a point. """

        # Do not draw if point is outsite the available area!
        if x>w:
            point.Hide()
            return
        point.MoveWindow(wx.Point(x,y), wx.Size(w,h))
        point.Show()

    #------------------------------------------------------------------------

    def __initializeColours(self):
        """ Create the pens and brush with default colors. """

        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self._penbordercolor = wx.Pen(wx.RED,2,wx.SOLID)

    #------------------------------------------------------------------------

    def __initialSize(self, size):
        """ Initialize the size. """

        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        if size:
            (w,h) = size
            if w < MIN_W: w = MIN_W
            if h < MIN_H: h = MIN_H
            self.SetSize(wx.Size(w,h))

    #------------------------------------------------------------------------

    def _calcW(self, duration):
        return int( duration * float(self._pxsec))

    #------------------------------------------------------------------------

    def __getTextWidth(self, text):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent(text)[0]

    #------------------------------------------------------------------------
