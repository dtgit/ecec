#
# API Tests
#

from Products.LinguaPlone.tests import LinguaPloneTestCase
from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation
from Products.LinguaPlone.tests.utils import sortTuple

from Products.LinguaPlone.public import AlreadyTranslated

import transaction

class TestAPI(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        self.addLanguage('de')
        self.addLanguage('fr')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'doc')
        self.english.setLanguage('en')
        self.alsoenglish = makeContent(self.folder, 'SimpleType', 'doctwo')
        self.alsoenglish.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')
        self.french = makeContent(self.folder, 'SimpleType', 'frenchdoc')
        self.french.setLanguage('fr')
        self.folder_en = makeContent(self.folder, 'SimpleFolder', 'folder')
        self.folder_en.setLanguage('en')

    def testEnglishIsCanonical(self):
        self.assertEqual(self.english.isCanonical(), True)

    def testEnglishIsTranslation(self):
        self.assertEqual(self.english.isTranslation(), True)

    def testGermanIsNotCanonical(self):
        self.assertEqual(self.german.isCanonical(), False)

    def testGermanIsTranslation(self):
        self.assertEqual(self.german.isTranslation(), True)

    def testGetCanonicalFromCanonicalObject(self):
        self.assertEqual(self.english, self.english.getCanonical())

    def testGetCanonicalFromNonCanonicalObject(self):
        self.assertEqual(self.english, self.german.getCanonical())

    def testCanonicalGetLanguage(self):
        self.assertEqual(self.english.getLanguage(), 'en')

    def testNonCanonicalGetLanguage(self):
        self.assertEqual(self.german.getLanguage(), 'de')

    def testCanonicalHasTranslationForEnglish(self):
        self.failUnless(self.english.hasTranslation('en'))

    def testCanonicalHasTranslationForGerman(self):
        self.failUnless(self.english.hasTranslation('de'))

    def testCanonicalHasNoTranslationForFrench(self):
        self.failIf(self.english.hasTranslation('fr'))

    def testNonCanonicalHasTranslationForEnglish(self):
        self.failUnless(self.german.hasTranslation('en'))

    def testNonCanonicalHasTranslationForGerman(self):
        self.failUnless(self.german.hasTranslation('de'))

    def testNonCanonicalHasNoTranslationForFrench(self):
        self.failIf(self.german.hasTranslation('fr'))

    def testCanonicalSetLanguageRaiseAlreadyTranslated(self):
        self.assertRaises(AlreadyTranslated, self.english.setLanguage, 'de')

    def testNonCanonicalSetLanguageRaiseAlreadyTranslated(self):
        self.assertRaises(AlreadyTranslated, self.german.setLanguage, 'en')

    def testAddTranslationReferenceToDifferentType(self):
        self.assertRaises(ValueError,
                self.french.addTranslationReference, self.folder_en)

    def testCanonicalAddTranslationReferenceRaiseAlreadyTranslated(self):
        self.assertRaises(AlreadyTranslated,
                self.english.addTranslationReference, self.english)
        self.assertRaises(AlreadyTranslated,
                self.english.addTranslationReference, self.alsoenglish)

    def testCanonicalAddTranslationRaiseAlreadyTranslated(self):
        self.assertRaises(AlreadyTranslated, self.english.addTranslation, 'en')

    def testNonCanonicalAddTranslationRaiseAlreadyTranslated(self):
        self.assertRaises(AlreadyTranslated, self.german.addTranslation, 'en')

    def testMakeTranslationCreateDifferentObjects(self):
        self.failIfEqual(self.english, self.german)

    def testMakeTranslationCreateSecondTranslation(self):
        self.french = makeTranslation(self.english, 'fr')
        self.failIfEqual(self.english, self.french)
        self.failIfEqual(self.german, self.french)
        self.assertEqual(self.french.getLanguage(), 'fr')

    def testGetCanonicalLanguageFromCanonicalObject(self):
        self.assertEqual('en', self.english.getCanonicalLanguage())

    def testGetCanonicalLanguageFromNonCanonicalObject(self):
        self.assertEqual('en', self.german.getCanonicalLanguage())

    def testGetTranslationFromCanonicalReturnLanguageObject(self):
        self.assertEqual(self.german, self.english.getTranslation('de'))

    def testGetTranslationFromNonCanonicalReturnLanguageObject(self):
        self.assertEqual(self.german, self.german.getTranslation('de'))

    def testGetTranslationWithMultipleLanguages(self):
        self.french = makeTranslation(self.german, 'fr')
        self.assertEqual(self.french, self.german.getTranslation('fr'))
        self.assertEqual(self.french, self.english.getTranslation('fr'))
        self.assertEqual(self.german, self.french.getTranslation('de'))
        self.assertEqual(self.german, self.english.getTranslation('de'))
        self.assertEqual(self.english, self.german.getTranslation('en'))
        self.assertEqual(self.english, self.french.getTranslation('en'))

    def testChangeCanonical(self):
        self.german.setCanonical()
        self.failIf(self.english.isCanonical())
        self.failUnless(self.german.isCanonical())
        self.assertEqual('de', self.english.getCanonicalLanguage())
        self.assertEqual('de', self.german.getCanonicalLanguage())
        self.assertEqual(self.german, self.english.getCanonical())
        self.assertEqual(self.german, self.german.getCanonical())
        self.french = makeTranslation(self.german, 'fr')
        self.french.setCanonical()
        self.failIf(self.english.isCanonical())
        self.failIf(self.german.isCanonical())
        self.failUnless(self.french.isCanonical())
        self.assertEqual('fr', self.english.getCanonicalLanguage())
        self.assertEqual('fr', self.french.getCanonicalLanguage())
        self.assertEqual('fr', self.german.getCanonicalLanguage())
        self.assertEqual(self.french, self.english.getCanonical())
        self.assertEqual(self.french, self.french.getCanonical())
        self.assertEqual(self.french, self.german.getCanonical())
        self.english.setCanonical()
        self.failUnless(self.english.isCanonical())
        self.failIf(self.german.isCanonical())
        self.failIf(self.french.isCanonical())
        self.assertEqual('en', self.english.getCanonicalLanguage())
        self.assertEqual('en', self.french.getCanonicalLanguage())
        self.assertEqual('en', self.german.getCanonicalLanguage())
        self.assertEqual(self.english, self.english.getCanonical())
        self.assertEqual(self.english, self.french.getCanonical())
        self.assertEqual(self.english, self.german.getCanonical())

    def testGetTranslationLanguages(self):
        languages = self.english.getTranslationLanguages()
        self.assertEqual(sortTuple(('en','de')), sortTuple(languages))

    def testGetTranslations(self):
        translations = self.english.getTranslations()
        self.assertEqual(translations['en'][0], self.english)
        self.assertEqual(translations['en'][1], 'private')
        self.assertEqual(translations['de'][0], self.german)
        self.assertEqual(translations['de'][1], 'private')

    def testReferences(self):
        reftool = self.portal.reference_catalog
        ref = reftool.getReferences(self.german, 'translationOf')[0]
        self.assertEqual(self.german, ref.getSourceObject())
        self.assertEqual(self.english, ref.getTargetObject())
        self.assertEqual(self.german, self.english.getBRefs('translationOf')[0])
        self.assertEqual(self.english, self.german.getRefs('translationOf')[0])

    def testRenameTranslation(self):
        transaction.savepoint(optimistic=True)
        self.folder.manage_renameObject(self.german.getId(), 'foo')
        self.failUnless('de' in self.english.getTranslationLanguages())
        self.assertEqual(self.english.getTranslation('de').getId(), 'foo')

    def testCanonicalInvalidateTranslations(self):
        self.english.invalidateTranslations()
        self.failIf(self.english.isOutdated())
        self.failUnless(self.german.isOutdated())

    def testTranslationInvalidateTranslations(self):
        self.german.invalidateTranslations()
        self.failIf(self.english.isOutdated())
        self.failUnless(self.german.isOutdated())

    def testRemoveTranslationNonCanonical(self):
        self.english.removeTranslation('de')
        self.failIf(self.english.getTranslation('de'))

    def testRemoveTranslationCanonical(self):
        self.french = makeTranslation(self.english, 'fr')
        self.german.removeTranslation('en')
        # German becomes the new Canonical
        self.failUnless(self.german.isCanonical())
        self.failIf(self.french.isCanonical())
        self.failIf(self.german.getTranslation('en'))
        self.failIf(self.french.getTranslation('en'))
        self.failUnless(self.german.getTranslation('fr'))

    def testProcessFormNotifyTranslations(self):
        self.failIf(self.german.isOutdated())
        self.english.processForm(values={'title':'English'})
        self.failUnless(self.german.isOutdated())
        self.german.processForm(values={'title':'German'})
        self.failIf(self.german.isOutdated())
        self.failIf(self.english.isOutdated())


class TestSetLanguage(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        self.addLanguage('de')
        self.addLanguage('fr')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'doc')
        self.english.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')

    def testCanonicalSetLanguage(self):
        self.english.setLanguage('fr')
        self.assertEqual(self.english.getLanguage(), 'fr')

    def testNonCanonicalSetLanguage(self):
        self.german.setLanguage('fr')
        self.assertEqual(self.german.getLanguage(), 'fr')

    def testCanonicalSetLanguageAddFrenchCanonical(self):
        self.english.setLanguage('fr')
        self.failUnless('fr' in self.english.getTranslationLanguages())

    def testCanonicalSetLanguageRemoveEnglishCanonical(self):
        self.english.setLanguage('fr')
        self.failIf('en' in self.english.getTranslationLanguages())

    def testCanonicalSetLanguageAddFrenchNonCanonical(self):
        self.english.setLanguage('fr')
        self.failUnless('fr' in self.german.getTranslationLanguages())

    def testCanonicalSetLanguageRemoveEnglishNonCanonical(self):
        self.english.setLanguage('fr')
        self.failIf('en' in self.german.getTranslationLanguages())

    def testNonCanonicalSetLanguageAddFrenchCanonical(self):
        self.german.setLanguage('fr')
        self.failUnless('fr' in self.english.getTranslationLanguages())

    def testNonCanonicalSetLanguageRemoveEnglishCanonical(self):
        self.german.setLanguage('fr')
        self.failIf('de' in self.english.getTranslationLanguages())

    def testNonCanonicalSetLanguageAddFrenchNonCanonical(self):
        self.german.setLanguage('fr')
        self.failUnless('fr' in self.german.getTranslationLanguages())

    def testCanonicalSetLanguageToNeutral(self):
        self.english.setLanguage('')
        self.assertEqual(self.english.getLanguage(), '')

    def testNonCanonicalSetLanguageToNeutral(self):
        self.german.setLanguage('')
        self.assertEqual(self.german.getLanguage(), '')

    def testThreeLanguagesCanonicalSetLanguageToNeutral(self):
        self.french = makeTranslation(self.english, 'fr')
        self.english.setLanguage('')
        self.failIf('en' in self.english.getTranslationLanguages())
        self.failIf('fr' in self.english.getTranslationLanguages())
        self.failIf('de' in self.english.getTranslationLanguages())
        self.failIf('en' in self.french.getTranslationLanguages())
        self.failIf('en' in self.german.getTranslationLanguages())

    def testThreeLanguagesNonCanonicalSetLanguageToNeutral(self):
        self.french = makeTranslation(self.english, 'fr')
        self.german.setLanguage('')
        self.failIf('de' in self.german.getTranslationLanguages())
        self.failIf('en' in self.german.getTranslationLanguages())
        self.failIf('fr' in self.german.getTranslationLanguages())
        self.failIf('de' in self.english.getTranslationLanguages())
        self.failIf('de' in self.french.getTranslationLanguages())

    def testSchemaUpdatePreserveLanguage(self):
        self.failUnless('en' in self.german.getTranslationLanguages())
        self.german._updateSchema()
        self.failUnless('en' in self.german.getTranslationLanguages())



class TestProcessFormRename(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        self.addLanguage('de')
        self.setLanguage('en')
        self.english = makeContent(self.folder, 'SimpleType', 'doc')
        self.english.setLanguage('en')
        self.german = makeTranslation(self.english, 'de')

    def testProcessFormRenameObject(self):
        transaction.savepoint(optimistic=True)
        # Fake a auto generated ID
        self.english.setId(self.portal.generateUniqueId('SimpleType'))
        self.english.processForm(values={'title':'I was renamed'})
        self.assertEqual(self.english.getId(), 'i-was-renamed')

    def testProcessFormRenameObjectOnlyFirstTime(self):
        transaction.savepoint(optimistic=True)
        # Fake a auto generated ID
        self.english.setId(self.portal.generateUniqueId('SimpleType'))
        self.english.processForm(values={'title':'Only First'})
        self.english.processForm(values={'title':'Not Second'})
        self.assertEqual(self.english.getId(), 'only-first')

    def testProcessFormRenameTranslation(self):
        transaction.savepoint(optimistic=True)
        self.german.processForm(values={'title':'Renamed Too'})
        self.assertEqual(self.german.getId(), 'renamed-too')

    def testProcessFormRenameTranslationOnlyFirstTime(self):
        transaction.savepoint(optimistic=True)
        self.german.processForm(values={'title':'Only First'})
        self.german.processForm(values={'title':'Not Second'})
        self.assertEqual(self.german.getId(), 'only-first')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPI))
    suite.addTest(makeSuite(TestSetLanguage))
    suite.addTest(makeSuite(TestProcessFormRename))
    return suite

