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
    """
    
    """

    def testIMSTransportInstall(self):
        """ Installation test """
        assert PloneTestCase.hasProduct('IMSTransport'), 'IMSTransport installation failure.'

    def testImport(self):
        """ Test that IMS import works for a default package. """
        self.setRoles(['Manager'])
        itt = self.portal.portal_IMSTransportTool
        self.portal.invokeFactory('Folder', 'testfolder')
        testfolder = getattr(self.portal, 'testfolder')
        results = itt.importZipfile(testfolder, 
                                    'Products/IMSTransport/tests/IMS_Sample_Course.zip', 
                                    'Default',
                                    'LOMv1.0')
        assert results[0], results[2]

        # Test sample folder
        assert getattr(testfolder, 'course')
        assert getattr(testfolder, 'course.html')

        # Test the sample page
        assert getattr(testfolder.course, 'sample-page')
        samplepage = getattr(testfolder.course, 'sample-page')

        assert 'Sample Page' == samplepage.Title()
        assert 'This is a sample page for IMS Packaging' == samplepage.Description()
        assert 'Ray, David' in samplepage.Creators()
        assert 'text/html' == samplepage.Format()
        assert 'Page' == samplepage.Type()
        assert '<h2>Sample Text</h2>' in samplepage.getText()
        
        # Test example subfolder
        assert getattr(testfolder.course, 'sample-folder')
        samplefolder = getattr(testfolder.course, 'sample-folder')
        assert 'sample-page-in-folder' in samplefolder.objectIds()
        sfolderpage = getattr(samplefolder, 'sample-page-in-folder')
        assert 'Page' == sfolderpage.Type()
        assert '<h2>My parent folder is Sample Folder</h2>' in sfolderpage.getText()

        # Test Sample file
        assert getattr(testfolder.course, 'samplefile.txt')
        samplefile = getattr(testfolder.course, 'samplefile.txt')
        assert 'Sample File' == samplefile.Title()
        assert 'This is a sample file for IMS Packaging.' == samplefile.Description()
        assert 'Ray, David' in samplefile.Creators()
        assert 'text/plain' == samplefile.Format()
        assert 'File' == samplefile.Type()
        assert samplefile.size() > 0

        # Test Sample image
        assert getattr(testfolder.course, 'sampleimage.gif')
        sampleimage = getattr(testfolder.course, 'sampleimage.gif')
        assert 'Sample Image' == sampleimage.Title()
        assert 'This is a sample image for IMS Packaging.' == sampleimage.Description()
        assert 'Ray, David' in sampleimage.Creators()
        assert 'image/gif' == sampleimage.Format()
        assert 'Image' == sampleimage.Type()
        assert sampleimage.size() > 0

    def testWebCTImport(self):
        """
        """
        self.setRoles(['Manager'])
        itt = self.portal.portal_IMSTransportTool
        self.portal.invokeFactory('Folder', 'testwctfolder')
        testwctfolder = getattr(self.portal, 'testwctfolder')
        results = itt.importZipfile(testwctfolder, 
                                    'Products/IMSTransport/tests/WebCTTest.zip', 
                                    'WebCT_import_xform',
                                    'LOMv1.0')
        assert results[0], results[2]

        assert getattr(testwctfolder, 'URL_8805229_R.html')
        testpage = getattr(testwctfolder, 'URL_8805229_R.html')
        assert 'assignments-external web' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<a href="http://cnn.com">assignments-external web</a>' in testpage.getText()
        
        assert getattr(testwctfolder, 'URL_8805232_R.html')
        testpage = getattr(testwctfolder, 'URL_8805232_R.html')
        assert 'syllabus-external web' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<a href="http://slashdot.org">syllabus-external web</a>' in testpage.getText()
        
        assert getattr(testwctfolder, 'URL_8805235_R.html')
        testpage = getattr(testwctfolder, 'URL_8805235_R.html')
        assert 'exams-external web' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<a href="http://slashdot.org">exams-external web</a>' in testpage.getText()

        assert getattr(testwctfolder, 'URL_8805241_R.html')
        testpage = getattr(testwctfolder, 'URL_8805241_R.html')
        assert 'External Website' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<a href="http://digg.com">External Website</a>' in testpage.getText()

        assert getattr(testwctfolder, 'CMD_8805178_R.html')
        testpage = getattr(testwctfolder, 'CMD_8805178_R.html')
        assert 'assignment worksheets' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<td><a href="COURSE_8805174_M/my_files/untitled.html">Put your title here</a></td>' in testpage.getText()

        assert getattr(testwctfolder, 'COURSE_8805174_M')
        testfolder = getattr(testwctfolder, 'COURSE_8805174_M')
        assert getattr(testfolder, 'my_files')
        my_files = getattr(testfolder, 'my_files')
        assert getattr(my_files, 'untitled.html')
        assert getattr(my_files, 'samplefile.txt')
        assert getattr(my_files, 'sampleimage.gif')
        assert getattr(my_files, 'untitled2.html')

        assert getattr(testwctfolder, 'CMD_8805179_R.html')
        testpage = getattr(testwctfolder, 'CMD_8805179_R.html')
        assert 'readings' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<td><a href="COURSE_8805174_M/my_files/untitled2.html">Put your title here</a></td>' in testpage.getText()

        assert getattr(testwctfolder, 'URL_8805290_R.html')
        testpage = getattr(testwctfolder, 'URL_8805290_R.html')
        assert 'Google' == testpage.Title()
        assert 'test_user_1_' in testpage.Creators()
        assert 'text/html' == testpage.Format()
        assert 'Page' == testpage.Type()
        assert '<a href="http://www.google.com">Google</a>' in testpage.getText()

    def testBBImport(self):
        """
        """
        self.setRoles(['Manager'])
        itt = self.portal.portal_IMSTransportTool
        self.portal.invokeFactory('Folder', 'testbbfolder')
        testbbfolder = getattr(self.portal, 'testbbfolder')
        results = itt.importZipfile(testbbfolder, 
                                    'Products/IMSTransport/tests/BBTest.zip', 
                                    'Blackboard_import_xform',
                                    'LOMv1.0')
        assert results[0], results[2]

        assert getattr(testbbfolder, 'res00001.html')
        testdocument = getattr(testbbfolder, 'res00001.html')
        assert 'COURSE_DEFAULT.CourseInformation.CONTENT_LINK.label' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00007.html">Test Image</a>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00005.html')
        testdocument = getattr(testbbfolder, 'res00005.html')
        assert 'Test Document' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert 'Hello World<p></p>\n' in testdocument.getText()

        assert getattr(testbbfolder, 'res00006.html')
        testdocument = getattr(testbbfolder, 'res00006.html')
        assert 'Test File' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert 'samplefile.txt' in testdocument.getText()

        assert getattr(testbbfolder, 'res00006')
        testfolder = getattr(testbbfolder, 'res00006')
        assert 'Folder' == testfolder.Type()
        assert getattr(testfolder, 'samplefile.txt')
        testfile = getattr(testfolder, 'samplefile.txt')
        assert 'Test File' == testfile.Title()
        assert 'test_user_1_' in testfile.Creators()
        assert 'text/plain' == testfile.Format()
        assert 'File' == testfile.Type()
        assert testfile.size() > 0

        assert getattr(testbbfolder, 'res00007.html')
        testdocument = getattr(testbbfolder, 'res00007.html')
        assert 'Test Image' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert 'sampleimage.gif' in testdocument.getText()

        assert getattr(testbbfolder, 'res00007')
        testfolder = getattr(testbbfolder, 'res00007')
        assert 'Folder' == testfolder.Type()
        assert getattr(testfolder, 'sampleimage.gif')
        testimage = getattr(testfolder, 'sampleimage.gif')
        assert 'Test Image' == testimage.Title()
        assert 'test_user_1_' in testimage.Creators()
        assert 'image/gif' == testimage.Format()
        assert 'Image' == testimage.Type()
        assert testimage.size() > 0

        assert getattr(testbbfolder, 'res00009.html')
        testdocument = getattr(testbbfolder, 'res00009.html')
        assert 'Test Document 2' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert 'Another test<p></p>\n' == testdocument.getText()

        assert getattr(testbbfolder, 'res00002.html')
        testdocument = getattr(testbbfolder, 'res00002.html')
        assert 'COURSE_DEFAULT.CourseDocuments.CONTENT_LINK.label' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00010.html">Test Document</a>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00010.html')
        testdocument = getattr(testbbfolder, 'res00010.html')
        assert 'Test Document' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00010//course.html" title="course.html">' in testdocument.getText()

        assert getattr(testbbfolder, 'res00010')
        testfolder = getattr(testbbfolder, 'res00010')
        assert 'Folder' == testfolder.Type()
        assert getattr(testfolder, 'course.html')
        testdocument = getattr(testfolder, 'course.html')
        assert 'Test Document' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<h3>COURSE TITLE</h3>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00003.html')
        testdocument = getattr(testbbfolder, 'res00003.html')
        assert 'COURSE_DEFAULT.Assignments.CONTENT_LINK.label' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00011.html">Test Document</a>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00011.html')
        testdocument = getattr(testbbfolder, 'res00011.html')
        assert 'Test Document' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert 'Hello World<p></p>\n' in testdocument.getText()

        assert getattr(testbbfolder, 'res00002.html')
        testdocument = getattr(testbbfolder, 'res00002.html')
        assert 'COURSE_DEFAULT.CourseDocuments.CONTENT_LINK.label' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00010.html">Test Document</a>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00004.html')
        testdocument = getattr(testbbfolder, 'res00004.html')
        assert 'COURSE_DEFAULT.ExternalLinks.CONTENT_LINK.label' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="res00012.html">Slashdot</a>' in testdocument.getText()

        assert getattr(testbbfolder, 'res00012.html')
        testdocument = getattr(testbbfolder, 'res00012.html')
        assert 'Slashdot' == testdocument.Title()
        assert 'test_user_1_' in testdocument.Creators()
        assert 'text/html' == testdocument.Format()
        assert 'Page' == testdocument.Type()
        assert '<a href="http://slashdot.org">Slashdot</a><p></p>\n' in testdocument.getText()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(testIMSTransport))
    return suite

if __name__ == '__main__':
    framework()
