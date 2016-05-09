#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import resources.rutils as rutils

LowerDict = {}
LowerDict[u'A'] = u'a'
LowerDict[u'B'] = u'b'
LowerDict[u'C'] = u'c'
LowerDict[u'D'] = u'd'
LowerDict[u'E'] = u'e'
LowerDict[u'F'] = u'f'
LowerDict[u'G'] = u'g'
LowerDict[u'H'] = u'h'
LowerDict[u'I'] = u'i'
LowerDict[u'J'] = u'j'
LowerDict[u'K'] = u'k'
LowerDict[u'L'] = u'l'
LowerDict[u'M'] = u'm'
LowerDict[u'N'] = u'n'
LowerDict[u'O'] = u'o'
LowerDict[u'P'] = u'p'
LowerDict[u'Q'] = u'q'
LowerDict[u'R'] = u'r'
LowerDict[u'S'] = u's'
LowerDict[u'T'] = u't'
LowerDict[u'U'] = u'u'
LowerDict[u'V'] = u'v'
LowerDict[u'W'] = u'w'
LowerDict[u'X'] = u'x'
LowerDict[u'Y'] = u'y'
LowerDict[u'Z'] = u'z'
LowerDict[u'À'] = u'à'
LowerDict[u'Á'] = u'a'
LowerDict[u'Á'] = u'á'
LowerDict[u'Â'] = u'â'
LowerDict[u'Ã'] = u'a'
LowerDict[u'Ã'] = u'ã'
LowerDict[u'Ä'] = u'ä'
#LowerDict[u'Æ'] = u'ae'
LowerDict[u'Ç'] = u'ç'
LowerDict[u'È'] = u'è'
LowerDict[u'É'] = u'é'
LowerDict[u'Ê'] = u'ê'
LowerDict[u'Ë'] = u'ë'
LowerDict[u'Ì'] = u'ì'
LowerDict[u'Í'] = u'í'
LowerDict[u'Î'] = u'î'
LowerDict[u'Ï'] = u'ï'
#LowerDict[u'Ñ'] = u'n'
LowerDict[u'Ò'] = u'ò'
LowerDict[u'Ó'] = u'ó'
LowerDict[u'Ô'] = u'ô'
LowerDict[u'Õ'] = u'_'
LowerDict[u'Õ'] = u'õ'
LowerDict[u'Ö'] = u'ö'
LowerDict[u'Ù'] = u'ù'
LowerDict[u'Ú'] = u'u'
LowerDict[u'Ú'] = u'ú'
LowerDict[u'Û'] = u'û'
LowerDict[u'Ü'] = u'ü'
LowerDict[u'Ý'] = u'ý'
LowerDict[u'Ă'] = u'ă'
LowerDict[u'Đ'] = u'đ'
LowerDict[u'Ĩ'] = u'ĩ'
LowerDict[u'Ũ'] = u'ũ'
LowerDict[u'Ơ'] = u'ơ'
LowerDict[u'Ư'] = u'ư'
LowerDict[u'Ạ'] = u'ạ'
LowerDict[u'Ả'] = u'ả'
LowerDict[u'Ấ'] = u'ấ'
LowerDict[u'Ầ'] = u'ầ'
LowerDict[u'Ẩ'] = u'ẩ'
LowerDict[u'Ẫ'] = u'ẫ'
LowerDict[u'Ậ'] = u'ậ'
LowerDict[u'Ắ'] = u'ắ'
LowerDict[u'Ằ'] = u'ằ'
LowerDict[u'Ẳ'] = u'ẳ'
LowerDict[u'Ẵ'] = u'ẵ'
LowerDict[u'Ặ'] = u'ặ'
LowerDict[u'Ẹ'] = u'ẹ'
LowerDict[u'Ẻ'] = u'ẻ'
LowerDict[u'Ẽ'] = u'ẽ'
LowerDict[u'Ế'] = u'ế'
LowerDict[u'Ề'] = u'ề'
LowerDict[u'Ể'] = u'ể'
LowerDict[u'Ễ'] = u'ễ'
LowerDict[u'Ệ'] = u'ệ'
LowerDict[u'Ỉ'] = u'ỉ'
LowerDict[u'Ị'] = u'ị'
LowerDict[u'Ọ'] = u'ọ'
LowerDict[u'Ỏ'] = u'ỏ'
LowerDict[u'Ố'] = u'ố'
LowerDict[u'Ồ'] = u'ồ'
LowerDict[u'Ổ'] = u'ổ'
LowerDict[u'Ỗ'] = u'ỗ'
LowerDict[u'Ộ'] = u'ộ'
LowerDict[u'Ớ'] = u'ớ'
LowerDict[u'Ờ'] = u'ờ'
LowerDict[u'Ở'] = u'ở'
LowerDict[u'Ỡ'] = u'ỡ'
LowerDict[u'Ợ'] = u'ợ'
LowerDict[u'Ụ'] = u'ụ'
LowerDict[u'Ủ'] = u'ủ'
LowerDict[u'Ứ'] = u'ứ'
LowerDict[u'Ừ'] = u'ừ'
LowerDict[u'Ử'] = u'ử'
LowerDict[u'Ữ'] = u'ữ'
LowerDict[u'Ự'] = u'ự'
LowerDict[u'Ỳ'] = u'ỳ'
LowerDict[u'Ỵ'] = u'ỵ'
LowerDict[u'Ỷ'] = u'ỷ'
LowerDict[u'Ỹ'] = u'ỹ'

# ---------------------------------------------------------------------------
class TestRutils(unittest.TestCase):

    def test_lower(self):
        for key,value in LowerDict.iteritems():
            self.assertEqual( value, rutils.ToLower(key) )
        self.assertEqual( rutils.ToLower(u'Ỹ') , rutils.ToLower('Ỹ') )

    def test_strip(self):
        self.assertEqual( rutils.ToStrip(u'  \n Ỹ  \t\r   ỏ  ') , u'Ỹ ỏ' )

# End TestWordsList
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRutils)
    unittest.TextTestRunner(verbosity=2).run(suite)