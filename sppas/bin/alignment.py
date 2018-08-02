#!/usr/bin/env python
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

    bin.alignment.py
    ~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Run the alignment automatic annotation

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotations.Align.aligners as aligners
from sppas.src.annotations.Align.sppasalign import sppasAlign
from sppas.src.utils.fileutils import setup_logging

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -w file -i file -r dir -o file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="Alignment automatic annotation.")

parser.add_argument("-w",
                    metavar="file",
                    required=True,
                    help='Input audio file name')

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file name with the phonetization')

parser.add_argument("-I",
                    metavar="file",
                    required=False,
                    help='Input file name with the tokenization')

parser.add_argument("-r",
                    metavar="file",
                    required=True,
                    help='Directory of the acoustic model '
                         'of the language of the text')

parser.add_argument("-R",
                    metavar="file",
                    required=False,
                    help='Directory of the acoustic model of '
                         'the mother language of the speaker')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name with estimated alignments')

parser.add_argument("-a",
                    metavar="name",
                    required=False,
                    choices=aligners.aligner_names(),
                    default="julius",
                    help='Speech automatic aligner system: '
                         'julius, hvite, basic (default: julius)')

parser.add_argument("--basic",
                    action='store_true',
                    help="Perform basic alignment if the aligner fails")

parser.add_argument("--noclean",
                    action='store_true',
                    help="Do not remove working directory")

parser.add_argument("--noactivity",
                    action='store_true',
                    help="Do not generate Activity tier")

parser.add_argument("--nophntok",
                    action='store_true',
                    help="Do not generate PhnTokAlign tier")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable verbose.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.quiet:
    setup_logging(0, None)
else:
    setup_logging(30, None)

# ----------------------------------------------------------------------------
# Automatic alignment is here:
# ----------------------------------------------------------------------------

# Fix resources

# Acoustic model of the language of the text (required)
modelText = args.r
# Acoustic model of the mother language of the speaker (optional)
modelSpk = args.R
# Create aligner
a = sppasAlign(modelText, modelSpk)

# Fix options

a.set_clean(True)
if args.noclean:
    a.set_clean(False)

a.set_basic(False)
if args.basic:
    a.set_basic(True)

a.set_activity_tier(True)
if args.noactivity:
    a.set_activity_tier(False)

a.set_phntokalign_tier(True)
if args.nophntok:
    a.set_phntokalign_tier(False)

a.set_aligner(args.a)

# Run speech segmentation
a.run(args.i, args.I, args.w, args.o)
