#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_rutils    import TestRutils
from test_wordslst  import TestWordsList
from test_dict      import TestDictPron, TestDictRepl, TestMapping
from test_model     import TestInterpolate, TestAcModel

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestRutils))
testsuite.addTest(unittest.makeSuite(TestWordsList))
testsuite.addTest(unittest.makeSuite(TestDictPron))
testsuite.addTest(unittest.makeSuite(TestDictRepl))
testsuite.addTest(unittest.makeSuite(TestMapping))
testsuite.addTest(unittest.makeSuite(TestInterpolate))
testsuite.addTest(unittest.makeSuite(TestAcModel))

unittest.TextTestRunner(verbosity=2).run(testsuite)

