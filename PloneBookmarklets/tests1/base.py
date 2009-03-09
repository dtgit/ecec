from zope.testing import doctest
from unittest import TestSuite
from zope.testing.doctestunit import DocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Testing.ZopeTestCase import ZopeDocFileSuite
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite, installProduct

installProduct('PloneBookmarklets')
setupPloneSite(extension_profiles=['Products.PloneBookmarklets:default'])

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = 'Products.PloneBookmarklets'




