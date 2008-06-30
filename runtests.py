#!/usr/bin/env python

import unittest
from tests.imgservertests import persistencetests, domaintests, imgenginetests, webtests

if __name__ == "__main__":
    alltests = unittest.TestSuite((persistencetests.suite(), domaintests.suite(), imgenginetests.suite(), webtests.suite()))
    #unittest.main()
    runner = unittest.TextTestRunner()
    runner.run(alltests)

