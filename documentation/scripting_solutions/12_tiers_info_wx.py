#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and print information about tiers, 
               with GUI.

"""

# ----------------------------------------------------------------------------
# Get SPPAS API
# ----------------------------------------------------------------------------

import wx
import sys
import os.path
sys.path.append(os.path.join("..",".."))

import sppas.src.annotationdata.aio as aio
from sppas.src.annotationdata import Transcription

# ----------------------------------------------------------------------------
# WX Functions
# ----------------------------------------------------------------------------

def wxShowErrorMessage(message):
    """ Open a MessageDialog to print an error. """

    dlg = wx.MessageDialog(None, message, 'Error',  wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()


def wxAskItem( message, choices ):
    """ Return the index of the selected item in choices, or -1 if the user cancelled. """

    selection = -1
    dialog = wx.SingleChoiceDialog(None, message, "Script: Tier information", choices)
    if dialog.ShowModal() == wx.ID_OK:
        selection = dialog.GetSelection()
    dialog.Destroy()
    return selection


def wxGetDir():
    """ Open a DirDialog and return a directory name with its path. """

    dirname = ''
    dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() == wx.ID_OK:
        dirname = dialog.GetPath()
    dialog.Destroy()
    return dirname


def wxGetFile():
    """ Open a FileDialog and return a filename with its path. """

    dirname = ''
    filename = ''

    dlg = wx.FileDialog(None, "Choose a file", dirname, "", "*.*", wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetFilename()
        dirname = dlg.GetDirectory()
    dlg.Destroy()
    return os.path.join(dirname, filename)


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

def checkExtension(filename):
    """ Check if filename is supported by SPPAS. """

    # Split the extension from the path and normalise it to lowercase.
    ext = os.path.splitext(filename)[-1].lower()

    # Check
    return ext in aio.extensions


def checkFile(filename):
    """ Return True if everything is normal. """

    if len(filename) == 0: 
        return False
    if not checkExtension(filename): 
        return False
    
    return True


def printInfo(filename):
    """ Print information about tiers of a file. """

    print(filename)

    # Read the file.
    trs = aio.read(filename)

    # Print information about tiers
    for tier in trs:

        # Get the tier type
        if tier.IsPoint() is True:
           tiertype = "Point"
        elif tier.IsInterval() is True:
           tiertype = "Interval"
        else:
            tiertype = "Unknown"

        # Print all informations
        print(" * Name: {:s}".format(tier.GetName()))
        print("    - Type: {:s}".format(tiertype))
        print("    - Number of annotations: {:d}".format(len(tier)))
        print("    - From time: {:.4f}".format(tier.GetBeginValue()))
        print("    - To time: {:.4f} ".format(tier.GetEndValue()))

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    """ This is the main function. """

    # Ask whether the script will be applied on one file or
    # on all files of a directory.
    message = "Apply the script on:"
    choices = ['a single file', 'all files in a directory']
    item = wxAskItem(message,choices)

    if item == -1:
        sys.exit(0)

    elif item == 0:
        # Get a filename
        filename = wxGetFile()
        # the user said OK or Cancel?
        if len(filename) == 0:
            sys.exit(0)
        # Verify if the extension is correct
        if not checkExtension(filename):
            wxShowErrorMessage( "Unknown file extension." )
            sys.exit(1)
        # Now, do the job!
        printInfo(filename)

    elif item == 1:
        # Get a directory name
        dirname = wxGetDir()
        # Get the list of expected files in this directory
        files = [ f for f in os.listdir(dirname) if checkExtension(f) ]
        # Now, do the job, for each file!
        for f in files:
            printInfo(os.path.join(dirname,f))
            # Let the result until a key is pressed.
            raw_input("Press a key to continue")

    # Let the result until a key is pressed.
    raw_input("Press a key to exit")

# ----------------------------------------------------------------------------
# This is the python entry point:
# Here, we start the wxpython application and ask to execute the main function.
if __name__ == '__main__':
    app = wx.App()
    main()
    app.MainLoop()

# ----------------------------------------------------------------------------
