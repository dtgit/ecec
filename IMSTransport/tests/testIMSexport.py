import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import user_name
from AccessControl import Unauthorized

ZopeTestCase.installProduct('IMSTransport')

PloneTestCase.setupPloneSite(products=('IMSTransport',))

class testIMSTransport(PloneTestCase.PloneTestCase):   
    
    def testIMSTransportInstall(self):
        assert PloneTestCase.hasProduct('IMSTransport'), 'IMSTransport failed to install'
        
        
    def testExportImportPackage(self):
        self.setRoles(['Manager'])
        po = self.portal
        it_tool = self.portal.portal_IMSTransportTool

        self.testExportPackage()
        
        po.invokeFactory('Folder','testFolder2')
        test_folder2 = getattr(po, 'testFolder2')       
        it_tool.importZipfile(test_folder2,'var/mydoc.zip','Default')
   
        assert test_folder2.testFolder.Title() == 'MyFolder'
        assert test_folder2.testFolder.testDoc.Title() == 'MyDoc'
        assert test_folder2.testFolder.testDoc.Creators()[0] == 'Test User1'
        assert test_folder2.testFolder.testDoc.Creators()[1] == 'New User2'
        assert test_folder2.testFolder.testDoc.Description() == 'Test Description'
        

    def testExportPackage(self):
        self.setRoles(['Manager'])
        po = self.portal
        
        if hasattr(po, 'testFolder'):
            test_folder = getattr(po, 'testFolder')
        else:
            po.invokeFactory('Folder','testFolder')
            test_folder = getattr(po, 'testFolder')
            
        test_folder.setTitle('MyFolder')    
        test_folder.invokeFactory('Document', 'testDoc')
        test_doc = getattr(test_folder, 'testDoc')
        test_doc.setTitle('MyDoc')
        test_doc.setCreators('Test User1\nNew User2')
        test_doc.setExcludeFromNav(1)
        test_doc.setDescription('Test Description')
        
        it_tool = self.portal.portal_IMSTransportTool
        manifest = it_tool.exportZipfile(test_folder,'var/mydoc.zip')
        
        zf = file(manifest[1],'w')
        zf.write(manifest[0])
        zf.close()
        
    def testExportImportNonAsciiPackage(self):
        self.setRoles(['Manager'])
        po = self.portal
        it_tool = self.portal.portal_IMSTransportTool

        self.testExportNonAsciiPackage()
        
        po.invokeFactory('Folder','testFolder2')
        test_folder2 = getattr(po, 'testFolder2')       
        it_tool.importZipfile(test_folder2,'var/mydoc.zip','Default')
   
        assert test_folder2.testFolder.Title() == 'ñàбългарски'
        assert test_folder2.testFolder.testDoc.Title() == 'ñàбългарски'
        assert test_folder2.testFolder.testDoc.Creators()[0] == 'ñàбългарски'
        assert test_folder2.testFolder.testDoc.Creators()[1] == 'ñàбългарски ñàбългарски'
        assert test_folder2.testFolder.testDoc.Description() == 'ñàбългарски'
        

    def testExportNonAsciiPackage(self):
        self.setRoles(['Manager'])
        po = self.portal
        
        if hasattr(po, 'testFolder'):
            test_folder = getattr(po, 'testFolder')
        else:
            po.invokeFactory('Folder','testFolder')
            test_folder = getattr(po, 'testFolder')
            
        test_folder.setTitle('ñàбългарски')    
        test_folder.invokeFactory('Document', 'testDoc')
        test_doc = getattr(test_folder, 'testDoc')
        test_doc.setTitle('ñàбългарски')
        test_doc.setCreators('ñàбългарски\nñàбългарски ñàбългарски')
        test_doc.setExcludeFromNav(1)
        test_doc.setDescription('ñàбългарски')
        
        it_tool = self.portal.portal_IMSTransportTool
        manifest = it_tool.exportZipfile(test_folder,'var/mydoc.zip')
        
        zf = file(manifest[1],'w')
        zf.write(manifest[0])
        zf.close()
        




def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(testIMSTransport))
    return suite

if __name__ == '__main__':
    framework()
