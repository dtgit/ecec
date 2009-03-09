import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import user_name
from AccessControl import Unauthorized

ZopeTestCase.installProduct('PloneBookmarklets')

PloneTestCase.setupPloneSite(products=('PloneBookmarklets',))

class testPloneBookmarklets(PloneTestCase.PloneTestCase):
    def testPloneBookmarkletsInstall(self):
        assert PloneTestCase.hasProduct('PloneBookmarklets'), "PloneBookmarklets failed to install"

    def testPloneBookmarkletsGetSites(self):
	pb_tool = self.portal.portal_bookmarklets
 	assert len(pb_tool.getSites()) == len(pb_tool.AvailableSites), "PloneBookmarklets getSites() failed"

    def testPloneBookmarkletsLoggedIn(self):
        self.assertRaises(Unauthorized, self.portal.portal_bookmarklets.restrictedTraverse, 'manage_overview')
        

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(testPloneBookmarklets))
    return suite

if __name__ == '__main__':
    framework()
