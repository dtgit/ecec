
from zope.testing import doctest
from Products.PloneTestCase.PloneTestCase import setupPloneSite, installProduct
from Products.PloneTestCase.PloneTestCase import PloneTestCase, FunctionalTestCase

installProduct('ContentLicensing')
setupPloneSite(extension_profiles=['Products.ContentLicensing:default'])

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = "Products.ContentLicensing"

class ContentLicensingTestCase(PloneTestCase):
    """ Test Class """

class ContentLicensingFunctionalTestCase(FunctionalTestCase):
    """ Functional test class """
