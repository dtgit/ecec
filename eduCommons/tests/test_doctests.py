from base import prod, oflags, eduCommonsFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite
from unittest import TestSuite


def test_suite():
    suite = TestSuite()

    prefstest = FunctionalDocFileSuite('tests/prefs.txt',
                                       'tests/accessibility.txt',
                                       package=prod,
                                       test_class=eduCommonsFunctionalTestCase,
                                       optionflags=oflags)
                                                         
    suite.addTests((prefstest,))

    return suite
