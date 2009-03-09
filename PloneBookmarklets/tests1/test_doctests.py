from base import prod, oflags
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from unittest import TestSuite


def test_suite():
    suite = TestSuite()

    prefstest = FunctionalDocFileSuite('tests1/prefs.txt',
                                       package=prod,
                                       test_class=FunctionalTestCase,
                                       optionflags=oflags)
                                                         
    suite.addTests((prefstest,))

    return suite
