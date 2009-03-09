#
# Default Page Tests
#

from Products.LinguaPlone.tests import LinguaPloneTestCase
from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation


class TestFolderDefaultPage(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        LinguaPloneTestCase.LinguaPloneTestCase.afterSetUp(self)
        self.addLanguage('de')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'doc')
        self.english.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')

    def testOriginalBehavior(self):
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, None)

    def testEnglishAsDefault(self):
        self.folder.setDefaultPage(self.english.getId())
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, self.english.getId())

    def testGermanAsDefault(self):
        self.setLanguage('de')
        self.folder.setDefaultPage(self.english.getId())
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, self.german.getId())

    def testInvalidAsDefault(self):
        self.folder.setDefaultPage('pt')
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, None)


class TestPortalDefaultPage(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        LinguaPloneTestCase.LinguaPloneTestCase.afterSetUp(self)
        self.addLanguage('de')
        self.setLanguage('en')
        self.setRoles(['Manager'])
        self.english = makeContent(self.portal, 'SimpleType', 'doc')
        self.english.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')

    def testOriginalBehavior(self):
        result = self.portal.getDefaultPage()
        self.failUnlessEqual(result, 'front-page')

    def testEnglishAsDefault(self):
        self.portal.setDefaultPage(self.english.getId())
        result = self.portal.getDefaultPage()
        self.failUnlessEqual(result, self.english.getId())

    def testGermanAsDefault(self):
        self.setLanguage('de')
        self.portal.setDefaultPage(self.english.getId())
        result = self.portal.getDefaultPage()
        self.failUnlessEqual(result, self.german.getId())

    def testInvalidAsDefault(self):
        self.folder.setDefaultPage('pt')
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, None)


class TestIndexDefaultPage(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        LinguaPloneTestCase.LinguaPloneTestCase.afterSetUp(self)
        self.addLanguage('de')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'index_html')
        self.english.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')

    def testOriginalBehavior(self):
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, self.english.getId())

    def testEnglishAsDefault(self):
        self.folder.setDefaultPage(self.english.getId())
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, self.english.getId())

    def testGermanAsDefault(self):
        self.setLanguage('de')
        self.folder.setDefaultPage(self.english.getId())
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, self.german.getId())

    def testInvalidAsDefault(self):
        self.folder.setDefaultPage('pt')
        result = self.folder.getDefaultPage()
        self.failUnlessEqual(result, 'index_html')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderDefaultPage))
    suite.addTest(makeSuite(TestPortalDefaultPage))
    suite.addTest(makeSuite(TestIndexDefaultPage))
    return suite

