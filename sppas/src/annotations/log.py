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

    src.annotations.log.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
import datetime
import codecs
import logging
import os

import sppas
from sppas import encoding
from . import OK_ID, INFO_ID, WARNING_ID, IGNORE_ID, ERROR_ID
from .import t

# ----------------------------------------------------------------------------

ENABLED = ":INFO 1030: "
DISABLED = ":INFO 1031: "
VERSION = ":INFO 1032: "
URL = ":INFO 1033: "
CONTACT = ":INFO 1034: "
AUTO_ANNS = ":INFO 1035: "
DATE = ":INFO 1036: "
LANGUAGES = ":INFO 1037: "
SEL_FILES = ":INFO 1038: "
SEL_ANNS = ":INFO 1039: "
FILE_EXT = ":INFO 1040: "
STATUS_OK = ":INFO 1041: "
STATUS_INFO = ":INFO 1042: "
STATUS_WARNING = ":INFO 1043: "
STATUS_IGNORE = ":INFO 1044: "
STATUS_ERROR = ":INFO 1045: "

# ----------------------------------------------------------------------------


class sppasLog(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A log file utility class.

    Class to manage the SPPAS automatic annotations log file, which is also
    called the "Procedure Outcome Report".

    """
    STR_INDENT = " ... "
    STR_ITEM = "  - "
    MAX_INDENT = 10

    # ----------------------------------------------------------------------

    def __init__(self, parameters):
        """ Create a sppasLog instance and open an output stream to NULL.

        :param parameters: (sppasParam)

        """
        self.parameters = parameters
        self.logfp = codecs.open(os.devnull, 'w', encoding)

    # ----------------------------------------------------------------------
    # File management
    # ----------------------------------------------------------------------

    def close(self):
        """ Close the current output stream. """
        
        self.logfp.close()

    # ----------------------------------------------------------------------

    def create(self, filename):
        """ Create and open a new output stream.
        
        :param filename: (str) Output filename
        
        """
        try:
            self.close()
        except:
            pass
        
        self.logfp = codecs.open(filename, 'w', encoding)

    # ----------------------------------------------------------------------

    def open(self, filename):
        """ Open an existing file and set the output stream.
        
        :param filename: (str) Output filename
        
        """
        try:
            self.close()
        except:
            pass

        self.logfp = codecs.open(filename, 'a+', encoding)

    # ----------------------------------------------------------------------
    # Write data
    # ----------------------------------------------------------------------

    def print_step(self, step_number):
        """ Print a step name from its number.

        :param step_number: (1..N) Number of an annotation defined in a sppasParam instance.

        """
        try:
            self.logfp.seek(0, 2)  # force to write at the end of the file
            self.print_separator()
            self.logfp.write(' '*24 + self.parameters.get_step_name(step_number))
            self.print_newline()
            self.print_separator()
        except Exception as e:
            logging.info(str(e))

    # ----------------------------------------------------------------------

    def print_message(self, message, indent=0, status=None):
        """ Print a message at the end of the current output stream.

        :param  message: (str) text to print
        :param  indent: (int) is the number of indentation to apply to the message
        :param  status: (int) 0 means OK, 1 means WARNING, 2 means IGNORED, and
        -1 value means ERROR.

        """
        try:
            self.logfp.seek(0, 2)
            str_indent = sppasLog.get_indent_text(indent)
            status_text = sppasLog.get_status_text(status)
            self.logfp.write(str_indent + status_text + message)
            self.print_newline()
        except Exception as e:
            logging.info(str(e))

    # ----------------------------------------------------------------------

    def print_raw_text(self, text):
        """ Print a text at the end of the output stream.

        :param text: (str) text to print

        """
        try:
            self.logfp.seek(0, 2)  # write at the end of the file
            self.logfp.write(text)
        except Exception as e:
            logging.info(str(e))

    # ----------------------------------------------------------------------

    def print_newline(self):
        """ Print a carriage return in the output stream. """

        try:
            self.logfp.write('\n')
        except Exception:
            pass

    # ----------------------------------------------------------------------

    def print_separator(self):
        """ Print a line in the output stream. """

        try:
            self.logfp.write('-'*78)
            self.print_newline()
        except Exception:
            pass

    # ----------------------------------------------------------------------

    def print_stat(self, step_number, value=None):
        """ Print the statistics values for a step.

        :param step_number: (1..N)
        :param value: (str) A statistic value. Instead, print the status (enabled or disabled).

        """
        try:
            if value is None:
                if self.parameters.get_step_status(step_number):
                    value = t.gettext(ENABLED)
                else:
                    value = t.gettext(DISABLED)
            self.print_item(self.parameters.get_step_name(step_number), str(value))
        except Exception as e:
            logging.info(str(e))

    # ----------------------------------------------------------------------

    def print_item(self, main_info, second_info=None):
        """ Print an item in the output stream.

        :param main_info: (str) Main information to print
        :param second_info: (str) A secondary info to print

        """
        try:
            self.logfp.seek(0, 2)  # write at the end of the file
            self.logfp.write(sppasLog.STR_ITEM)
            self.logfp.write(main_info)
            if second_info is not None:
                self.logfp.write(': ')
                self.logfp.write(second_info)
            self.print_newline()
        except Exception as e:
            logging.info(str(e))

    # ----------------------------------------------------------------------

    def print_header(self):
        """ Print the parameters information in the output stream. """

        self.logfp.seek(0, 2)  # write at the end of the file
        self.print_message(sppas.__name__ + ' ' + t.gettext(VERSION) + ' ' + sppas.__version__)
        self.print_message(sppas.__copyright__)
        self.print_message(t.gettext(URL) + ': ' + sppas.__url__)
        self.print_message(t.gettext(CONTACT) + ': ' + sppas.__author__ + "(" + sppas.__contact__ + ")")
        self.print_newline()
        self.print_separator()

        self.print_message(' '*24 + t.gettext(AUTO_ANNS) + ': ')
        self.print_separator()
        self.print_newline()

        self.print_message(t.gettext(DATE) + ': ' + str(datetime.datetime.now()))
        self.print_message(t.gettext(LANGUAGES) + ': ')
        for i in range(self.parameters.get_step_numbers()):
            if self.parameters.get_lang(i) is not None:
                self.print_item(self.parameters.get_step_name(i), self.parameters.get_lang(i))
            else:
                self.print_item(self.parameters.get_step_name(i), "---")
        self.print_separator()
        self.print_newline()

        self.print_message(t.gettext(SEL_FILES) + ': ')
        for sinput in self.parameters.get_sppasinput():
            self.print_item(sinput)
        self.print_separator()
        self.print_newline()

        self.print_message(t.gettext(SEL_ANNS) + ': ')
        for i in range(self.parameters.get_step_numbers()):
            self.print_stat(i)
        self.print_separator()
        self.print_newline()

        self.print_message(t.gettext(FILE_EXT) + ': ' + self.parameters.get_output_format())
        self.print_newline()

    # ----------------------------------------------------------------------

    @staticmethod
    def get_status_text(status_id):
        """ Return a status text from a status identifier.

        :param status_id: (int)

        """
        if status_id is None:
            return ""

        status = ""
        if status_id == OK_ID:
            status = STATUS_OK

        elif status_id == WARNING_ID:
            status = STATUS_WARNING

        elif status_id == IGNORE_ID:
            status = STATUS_IGNORE

        elif status_id == INFO_ID:
            status = STATUS_INFO

        elif status_id == ERROR_ID:
            status = STATUS_ERROR

        return t.gettext(status)

    # ----------------------------------------------------------------------

    @staticmethod
    def get_indent_text(number):
        """ Return a string representing some indentation.

        :param number: (int) A positive integer.

        """
        number = int(number)
        if number > sppasLog.MAX_INDENT:
            number = sppasLog.MAX_INDENT
        if number < 0:
            number = 0
        return sppasLog.STR_INDENT * number
