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

    src.anndata.filter.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Filter system on annotations.

    Reference:

        | Brigitte Bigi, Jorane Saubesty (2015).
        | Searching and retrieving multi-levels annotated data,
        | Proceedings of Gesture and Speech in Interaction, Nantes (France).

    Example of use:

        >>> # extract pauses.
        >>> predicate = PatternMatching(exact="sp") | PatternMatching(exact="+")
        >>> annotations = [a for a in tier if predicate(a)]

        >>> # extract silences >= 250ms.
        >>> predicate = PatternMatching(exact="#") & PatternDuration(ge=0.250)
        >>> annotations = [a for a in tier if predicate(a)]

"""
from .patternmatch import PatternMatching
from .patterduration import PatternDuration

__all__ = [
    "PatternMatching",
    "PatternDuration"
]
