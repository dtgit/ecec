# Plone Solutions AS <info@plonesolutions.com>
# Martijn Pieters <mj@plonesolutions.com>
# http://www.plonesolutions.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from unittest import TestCase

from Products.CMFPlone.interfaces.Translatable import ITranslatable
from Products.CMFCore.interfaces.portal_catalog import IndexableObjectWrapper

class Dummy:
    __implements__ = (ITranslatable,)
    
    def __init__(self, cid, lang):
        self._cid = cid
        self._lang = lang

    def Language(self):
        return self._lang
    
    def getCanonical(self):
        # No mucking about with pointers, we only need to get a UID, which 
        # this dummy provides directly
        return self
    
    def UID(self):
        return self._cid

    def __str__( self ):
        return '<Dummy: %s (cid %s)>' % (self._lang, self._cid)
    
    def __len__(self):
        # Simulate an empty folder; older IndexableObjectWrapper test code
        # failed for empty folders. See 
        # http://www.nabble.com/Bug-in-LinguaPlone-tf3903725.html
        return 0

    __repr__ = __str__
    
class DummyIndexableObjectWrapper:
    __implements__ = (IndexableObjectWrapper,)
    def __init__(self, wrapped):
        self._IndexableObjectWrapper__ob = wrapped
        self._obj = wrapped
    
testdata = (
    # Translated content id 'abc'
    Dummy('abc', 'fr'),
    Dummy('abc', 'en'),
    Dummy('abc', 'en-gb'),
    Dummy('abc', 'en-us'),
    Dummy('abc', 'en-ca'),
    
    # Translated content id 'foo'
    Dummy('foo', 'fr'),
    Dummy('foo', 'en'),
    Dummy('foo', 'en-gb'),
    
    # Translated content id 'bar'
    Dummy('bar', 'fr'),
    Dummy('bar', 'en-gb'),
    Dummy('bar', 'en-ca'),
)

class TestLanguageIndex(TestCase):
    def setUp(self):
        from Products.LinguaPlone.LanguageIndex import LanguageIndex
        self.index = LanguageIndex('foo')
        
    def indexData(self):
        for i, entry in enumerate(testdata):
            self.index.index_object(i, entry)
            
    def search(self, tag, doIndex=True, fallback=None):
        if doIndex:
            self.indexData()
        query = dict(foo=tag)
        if fallback is not None:
            query['foo'] = dict(query=tag, fallback=fallback)
        result = list(self.index._apply_index(query)[0])
        result.sort()
        return result
        
    def testEmpty(self):
        self.assertEqual(len(self.index), 0)
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.indexSize(), 0)
        
        self.assertTrue(self.index.getEntryForObject(1234) is None)
        self.assertTrue(self.index._apply_index({'baz': 'bar'}) is None)
        
        result, attrs = self.index._apply_index({'foo': 'bar'})
        self.assertTrue(not result)
        self.assertEqual(attrs, ('Language',))
        
    def testEntryForObject(self):
        self.indexData()
        
        for i, dummy in enumerate(testdata):
            entry = self.index.getEntryForObject(i)
            self.assertEqual(str(entry), dummy.Language())
            self.assertEqual(entry.cid, dummy.UID())
        
    def testSimpleSearch(self):
        self.assertEqual(self.search('fr'), 
                         [0, 5, 8]) # All the 'fr' translations
        
    def testSubtagNoFallbacks(self):
        self.assertEqual(self.search('en-gb'), 
                         [2, 7, 9]) # All the 'en-gb' translations
        
    def testSubtagFallbacks(self):
        self.assertEqual(self.search('en-us'), 
                         [3, 6, 10]) # 'en-us', 'en' and 'en-ca'
        
    def testMainFallbacks(self):
        self.assertEqual(self.search('en'),
                         [1, 6, 10]) # 'en', 'en' and 'en-ca'
        
    def testUnindex(self):
        self.indexData()

        self.assertEqual(len(self.index), 11)
        
        self.index.unindex_object(0)
        self.index.unindex_object(5)
        self.index.unindex_object(8)
        
        self.assertEqual(len(self.index), 8)
        self.assertEqual(self.search('fr', False), [])
        
    def testReindex(self):
        self.indexData()
        self.index.index_object(0, testdata[0])
        
        self.assertEqual(len(self.index), 11)
        
        self.index.index_object(0, Dummy('abc', 'de'))
        self.assertEqual(self.search('de', False), [0])
        self.assertEqual(self.search('fr', False), [5, 8])
        
    def testQueryWithFallback(self):
        self.assertEqual(self.search('en', fallback=False), [1, 6])
        self.assertEqual(self.search('en', False, fallback=True), [1, 6, 10])
        
    def testFallbackProperty(self):
        self.index.fallback = False
        self.assertEqual(self.search('en'), [1, 6])
        self.assertEqual(self.search('en', False, fallback=False), [1, 6])
        self.assertEqual(self.search('en', False, fallback=True), [1, 6, 10])
        
    def testUniqueValues(self):
        self.indexData()
        result = list(self.index.uniqueValues())
        result.sort()
        self.assertEqual(result, ['en', 'en-ca', 'en-gb', 'en-us', 'fr'])
        
        self.index.unindex_object(0)
        self.index.unindex_object(5)
        self.index.unindex_object(8)
        
        result = list(self.index.uniqueValues())
        result.sort()
        self.assertEqual(result, ['en', 'en-ca', 'en-gb', 'en-us'])
        
    def testUniqueValuesLengths(self):
        self.indexData()
        result = list(self.index.uniqueValues(withLengths=True))
        result.sort()
        self.assertEqual(result, [('en', 2), ('en-ca', 2), ('en-gb', 3), 
                                  ('en-us', 1), ('fr', 3)])
        
    def testKeyForDocument(self):
        self.indexData()
        self.assertEqual(self.index.keyForDocument(0), 'fr')
        self.assertEqual(self.index.keyForDocument(4), 'en-ca')
        
    def testDocumentToKeyMap(self):
        self.indexData()
        map = self.index.documentToKeyMap()
        data = list(map.items())
        data.sort()
        self.assertEqual(data, 
                         [(0, 'fr'), (1, 'en'), (2, 'en-gb'), (3, 'en-us'),
                          (4, 'en-ca'), (5, 'fr'), (6, 'en'), (7, 'en-gb'),
                          (8, 'fr'), (9, 'en-gb'), (10, 'en-ca')])
        
    def testIndexableWrapper(self):
        dummy = Dummy('abc', 'en')
        wrapper = DummyIndexableObjectWrapper(dummy)
        
        self.assertEqual(self.index.index_object(0, wrapper), 1)
        
        del wrapper._IndexableObjectWrapper__ob
        self.assertEqual(self.index.index_object(0, wrapper), 1)
        
        del wrapper._obj
        self.assertEqual(self.index.index_object(0, wrapper), 0)
        
    def testNoLanguageMethod(self):
        class NoLanguageDummy(Dummy):
            def Language(self):
                raise AttributeError('Language')
                
        dummy = NoLanguageDummy('abc', None)
        self.assertEqual(self.index.index_object(0, dummy), 0)
        
    def testNoCallableLanguage(self):
        class NoCallableDummy(Dummy):
            Language = None
            
        dummy = NoCallableDummy('abc', None)
        self.assertEqual(self.index.index_object(0, dummy), 1)

class TestSplitLanguage(TestCase):
    def split(self, tag):
        from Products.LinguaPlone.utils import splitLanguage
        return splitLanguage(tag)
    
    def testOnlyMain(self):
        self.assertEqual(self.split('en'), ('en', None))
        
    def testSubtag(self):
        self.assertEqual(self.split('en-gb'), ('en', 'gb'))
        
    def testMultipleSubtags(self):
        self.assertEqual(self.split('fr-Latin1-ca'), ('fr', 'latin1-ca'))
        
    def testIPrefix(self):
        self.assertEqual(self.split('i-cherokee'), ('i-cherokee', None))
        
    def testXPrefix(self):
        self.assertEqual(self.split('x-pig-latin'), ('x-pig-latin', None))
        
    def testNonString(self):
        self.assertEqual(self.split(None), (None, None))
        self.assertEqual(self.split(1234), (None, None))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageIndex))
    suite.addTest(makeSuite(TestSplitLanguage))
    return suite
