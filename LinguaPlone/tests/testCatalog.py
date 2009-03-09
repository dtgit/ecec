#
# Catalog Tests
#

from Products.LinguaPlone.tests import LinguaPloneTestCase
from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation


class TestMultilingualCatalog(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        LinguaPloneTestCase.LinguaPloneTestCase.afterSetUp(self)
        self.addLanguage('de')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'doc')
        self.english.edit(title='Foo', language='en')
        self.german = makeTranslation(self.english, 'de')
        self.german.edit(title='Foo')
        self.catalog = self.portal.portal_catalog

    def testSearchEnglish(self):
        search = self.catalog(Language='en')
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failIf(self.german in [x.getObject() for x in search])

    def testSearchGerman(self):
        search = self.catalog(Language='de')
        self.failIf(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testSearchAll(self):
        search = self.catalog(Language='all')
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testSearchTitleEnglish(self):
        search = self.catalog(Title='Foo')
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failIf(self.german in [x.getObject() for x in search])

    def testSearchTitleGerman(self):
        self.setLanguage('de')
        search = self.catalog(Title='Foo')
        self.failIf(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testSearchAllAndTitle(self):
        search = self.catalog(Language='all', Title='Foo')
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testSearchAllAndBadTitle(self):
        search = self.catalog(Language='all', Title='Bar')
        self.failIf(self.english in [x.getObject() for x in search])
        self.failIf(self.german in [x.getObject() for x in search])

    def testSearchGermanAndTitle(self):
        search = self.catalog(Language='de', Title='Foo')
        self.failIf(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testMultipleLanguages(self):
        search = self.catalog(Language=['en', 'de'])
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])

    def testMultipleLanguagesAndTitle(self):
        search = self.catalog(Language=['en', 'de'], Title='Foo')
        self.failUnless(self.english in [x.getObject() for x in search])
        self.failUnless(self.german in [x.getObject() for x in search])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMultilingualCatalog))
    return suite

