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
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
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
# ---------------------------------------------------------------------------
# File: tokenize.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from annotations.Token.tok import sppasTok
from annotations.Token.tokenize import DictTok
from resources.wordslst import WordsList
from resources.dictrepl import DictRepl

from sp_glob import RESOURCES_PATH


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

epilogue  = "!!!!!!!  if no input is given, the input is stdin and output is stdout  !!!!!!!\n"
epilogue += "!!!!!!!  if no output is given, the output is the input  !!!!!!!"

parser = ArgumentParser(usage="%s -r vocab [options]" % os.path.basename(PROGRAM), prog=PROGRAM, description="Text normalization command line interface.", epilog=epilogue)

parser.add_argument("-r", "--vocab", required=True, help='Vocabulary file name')
parser.add_argument("-i", metavar="file", required=False, help='Input file name')
parser.add_argument("-o", metavar="file", required=False, help='Output file name')
parser.add_argument("--delimiter", metavar='char', help="Use a delimiter character instead of a space for word delimiter.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Automatic Tokenization is here:
# ----------------------------------------------------------------------------

base = os.path.basename( args.vocab )
lang = base[:3]

delim = ' '
if args.delimiter:
    delim = unicode(args.delimiter)

if args.i:
    p = sppasTok( args.vocab,lang )
    p.tokenizer.set_delim( delim )
    p.run( args.i, args.o )

else:

    vocab = WordsList( args.vocab )
    tokenizer = DictTok( vocab,lang )

    try:
        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", lang + ".repl"), nodump=True)
        tokenizer.set_repl( repl )
    except Exception as e:
        print "[warning] No replacement dictionary: ",str(e)
    try:
        punct = WordsList(os.path.join(RESOURCES_PATH, "vocab", "Punctuations.txt"), nodump=True )
        tokenizer.set_punct( punct )
    except Exception as e:
        print "[warning] No punctuation dictionary: ",str(e)

    tokenizer.set_delim( delim )

    for line in sys.stdin:
        print tokenizer.tokenize( line ).encode('utf8')

# ----------------------------------------------------------------------------
