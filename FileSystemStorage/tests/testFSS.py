## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Testing FSS features
$Id: testFSS.py 54530 2007-11-27 09:22:03Z yboussard $
"""

from common import *
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from StringIO import StringIO


class TestFSS(FSSTestCase.FSSTestCase):
    def afterSetUp(self):
        self.loginAsPortalOwner()
        content_id = 'test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=content_id)
        self.test_folder = getattr(self.portal, content_id)
        self.logout()

# #############################################################################
# ADD
# #############################################################################

    def testAddFileFromString(self):
        self.loginAsPortalOwner()
        content_id = 'test_file'
        self.file_content = self.addFileByString(self.test_folder, content_id)

        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test value
        self.assertEquals(str(file_value.data), 'mytestfile')

        # Test filename
        self.assertEquals(file_value.filename, '')

        # Test size
        self.assertEquals(file_value.get_size(), 10)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'text/plain')

        # Test using BaseUnit
        bu = file_field.getBaseUnit(self.file_content)
        bu_value = bu.getRaw()
        self.assertEquals(len(bu_value), 10)
        self.assertEquals(bu_value, """mytestfile""")

        # Test using manage_FTPget
        ftp_value = self.file_content.manage_FTPget()
        self.failIf(ftp_value is None)
        self.assertEquals(len(ftp_value), 10)
        self.assertEquals(ftp_value, """mytestfile""")
        self.logout()

    def _testDefaultContentFromUploadedFile(self):
        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'application/msword')

        # Test using BaseUnit
        bu = file_field.getBaseUnit(self.file_content)
        bu_value = bu.getRaw()
        self.assertEquals(len(bu_value), 10240)

        # Test using manage_FTPget
        ftp_value = self.file_content.manage_FTPget()
        self.failIf(ftp_value is None)
        self.assertEquals(len(ftp_value), 10240)

    def testAddFileFromUploadedFile(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        self._testDefaultContentFromUploadedFile()

        self.logout()

# #############################################################################
# EDIT
# #############################################################################
    def testEditFile(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        self._testDefaultContentFromUploadedFile()

        # Update content
        data_path = self.getDataPath()
        self.updateContent(self.file_content, 'file', os.path.join(data_path, 'excel.xls'))

        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'excel.xls')

        # Test size
        self.assertEquals(file_value.get_size(), 13824)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'application/vnd.ms-excel')

        self.logout()

# #############################################################################
# RENAME
# #############################################################################
    def testRenameContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)
        old_uid = self.file_content.UID()

        # Rename file
        new_content_id = 'new_test_file'
        self.test_folder.manage_renameObjects((content_id,), (new_content_id,))

        # Test file
        self.assertEquals(self.file_content.getId(), new_content_id)
        self.assertEquals(self.file_content.UID(), old_uid)
        self._testDefaultContentFromUploadedFile()
        self.logout()

# #############################################################################
# COPY
# #############################################################################
    def testCopyContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Copy file in another folder
        cb = self.test_folder.manage_copyObjects(ids=(content_id,))

        new_folder_id = 'new_test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=new_folder_id)
        new_folder = getattr(self.portal, new_folder_id)

        # Paste
        new_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test source file
        self._testDefaultContentFromUploadedFile()

        # Test destination file
        new_file_content = getattr(new_folder, content_id)

        # Get file field
        file_field = new_file_content.getField('file')

        # Get file value
        file_value = file_field.get(new_file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_file_content), 'application/msword')

        # more tests here to test that the external content
        # is also copied
        old_storage = getattr(self.test_folder, content_id).getField('file').getStorage()
        new_storage = file_field.getStorage()
        old_instance = getattr(self.test_folder, content_id)

        old_fss = old_storage.getFSSInfo('file', old_instance)
        new_fss = new_storage.getFSSInfo('file', new_file_content)

        old_brains = self.fss_tool.getStorageBrainsByUID(old_fss.getUID())
        new_brains = self.fss_tool.getStorageBrainsByUID(new_fss.getUID())

        st_old = [x for x in old_brains if x['name'] == 'file'][0]
        st_new = [x for x in new_brains if x['name'] == 'file'][0]

        self.assertNotEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertNotEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])
        self.assertNotEqual(st_old['path'], st_new['path'])

        self.logout()

    def testCopyFolderWithImages(self):
        if not self.use_atct:
            # Only ATFolder implements correctly copy/paste for sub objects
            return

        self.loginAsPortalOwner()

        # Create new folder and fill it with some content
        self.portal.invokeFactory(id='test_source_folder', type_name=FOLDER_TYPE)
        self.sf = getattr(self.portal, 'test_source_folder')

        # adding some images
        self.addImageByFileUpload(self.sf, 's1')
        self.addImageByFileUpload(self.sf, 's2')
        self.addImageByFileUpload(self.sf, 's3')
        self.addImageByFileUpload(self.sf, 's4')
        self.addImageByFileUpload(self.sf, 's5')
        self.addImageByFileUpload(self.sf, 's6')

        self.assertEqual(len(self.sf.objectValues()), 6)

        # creating new subfolder
        self.portal.invokeFactory(id='test_target_folder', type_name=FOLDER_TYPE)

        # make sure objects got copied
        obnum = random.choice([1,2,3,4,5,6])

        o_cobject = getattr(self.sf, 's%s' % obnum)
        o_storage = o_cobject.getField('image').getStorage()
        o_fssinfo = o_storage.getFSSInfo('image', o_cobject)
        o_brains = self.fss_tool.getStorageBrainsByUID(o_fssinfo.getUID())

        # copying complete sf folder to test_target_folder
        cb = self.portal.manage_copyObjects(ids=(self.sf.getId(), ))

        # paste into new folder
        self.tf = getattr(self.portal, 'test_target_folder')
        self.assertEqual(len(self.tf.objectValues()), 0)
        self.tf.manage_pasteObjects(cb_copy_data=cb)
        self.assertEqual(len(self.tf.objectValues()), 1)

        # copied folder should contain six items
        self.cf = getattr(self.tf, 'test_source_folder')
        self.assertEqual(len(self.cf.objectValues()), 6)

        # make sure copied folder got new UID
        self.assertNotEqual(self.cf.getPhysicalPath(), self.sf.getPhysicalPath())
        self.assertEqual(self.cf.getId(), self.sf.getId())

        n_cobject = getattr(self.cf, 's%s' % obnum)
        n_storage = n_cobject.getField('image').getStorage()
        n_fssinfo = n_storage.getFSSInfo('image', n_cobject)
        n_brains = self.fss_tool.getStorageBrainsByUID(n_fssinfo.getUID())

        self.assertNotEqual(o_fssinfo.getUID(), n_fssinfo.getUID())
        self.assertNotEqual(len(o_brains), 0, str(o_brains))
        self.assertNotEqual(len(n_brains), 0, str(n_brains))

        # test if scales were copied
        for name in ('image_mini', 'image_thumb'):
            fs_path = [x['fs_path'] for x in o_brains if x['name'] == name][0]
            assert os.path.exists(fs_path)

        for name in ('image_mini', 'image_thumb'):
            fs_path = [x['fs_path'] for x in n_brains if x['name'] == name][0]
            assert os.path.exists(fs_path)

        # FSS must have created new files on filesystem
        for name in ('image', 'image_mini', 'image_thumb'):
            o_brain = [x for x in o_brains if x['name'] == name][0]
            n_brain = [x for x in n_brains if x['name'] == name][0]
            self.assertNotEqual(o_brain['fs_path'], n_brain['fs_path'])
            self.assertEqual(o_brain['size'], n_brain['size'])
            self.assertNotEqual(o_brain['path'], n_brain['path'])

        # testing deletion
        old_s1_uid = self.sf.s1.UID()
        s1_brains = self.fss_tool.getStorageBrainsByUID(old_s1_uid)
        assert len(s1_brains)>0

        self.sf.manage_delObjects(['s1', ])
        assert 's1' not in self.sf.objectIds()
        s1_brains = self.fss_tool.getStorageBrainsByUID(old_s1_uid)
        assert len(s1_brains)==0


        self.logout()

# #############################################################################
# CUT
# #############################################################################
    def testCutContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)
        old_uid = self.file_content.UID()
        old_storage = getattr(self.test_folder, content_id).getField('file').getStorage()
        old_instance = getattr(self.test_folder, content_id)
        old_fss = old_storage.getFSSInfo('file', old_instance)

        # Copy file in another folder
        cb = self.test_folder.manage_cutObjects(ids=(content_id,))

        new_folder_id = 'new_test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=new_folder_id)
        new_folder = getattr(self.portal, new_folder_id)

        # Paste
        new_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test source file
        self.failIf(hasattr(self.test_folder, content_id))

        # Test destination file
        new_file_content = getattr(new_folder, content_id)

        # Get file field
        file_field = new_file_content.getField('file')

        # Get file value
        file_value = file_field.get(new_file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_file_content), 'application/msword')

        self.assertEquals(new_file_content.UID(), old_uid)

        # more tests here to test that the external content
        # is also copied
        new_storage = file_field.getStorage()
        new_fss = new_storage.getFSSInfo('file', new_file_content)

        st_old = self.fss_tool.getStorageBrainsByUID(old_fss.getUID())[0]
        st_new = self.fss_tool.getStorageBrainsByUID(new_fss.getUID())[0]

        self.assertEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])

        self.logout()

    def testCutFolderWithFSSContent(self):
        self.loginAsPortalOwner()

        # Create source folder
        src_folder_id = 'src_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=src_folder_id)
        src_folder = getattr(self.portal, src_folder_id)

        # Create a file in source folder
        src_content_id = 'src_file'
        src_content = self.addFileByFileUpload(src_folder, src_content_id)

        # Keep a reference to this source content
        old_instance = src_content
        old_uid = old_instance.UID()
        old_storage = old_instance.getField('file').getStorage()
        old_fss = old_storage.getFSSInfo('file', old_instance)

        # Copy source folder to another folder
        cb = self.portal.manage_cutObjects(ids=(src_folder_id,))

        dst_folder_id = 'dst_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=dst_folder_id)
        dst_folder = getattr(self.portal, dst_folder_id)

        # Paste
        dst_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test that source folder has moved
        self.failIf(hasattr(self.portal, src_folder_id))

        # Get new source folder
        new_folder = getattr(dst_folder, src_folder_id)

        # Get new source content
        new_content = getattr(new_folder, src_content_id)

        # Get file field
        file_field = new_content.getField('file')

        # Get file value and test it
        file_value = file_field.get(new_content)
        self.failUnless(isinstance(file_value, VirtualBinary), file_value.__class__)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_content), 'application/msword')

        self.assertEquals(new_content.UID(), old_uid)

        # more tests here to test that the external content
        # is also copied
        new_storage = file_field.getStorage()
        new_fss = new_storage.getFSSInfo('file', new_content)

        st_old = self.fss_tool.getStorageBrainsByUID(old_fss.getUID())[0]
        st_new = self.fss_tool.getStorageBrainsByUID(new_fss.getUID())[0]

        self.assertEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])

        self.logout()

# #############################################################################
# DELETE
# #############################################################################
    def testDeleteContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Delete file
        self.test_folder.manage_delObjects(ids=[content_id])

        # Test file
        self.failIf(hasattr(self.test_folder, content_id))
        self.logout()

# #############################################################################
# FIELD OPERATIONS
# #############################################################################
    def testDeleteField(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Delete file field value
        file_field.set(file_content, 'DELETE_FILE')

        # Get file value
        file_value = file_field.get(file_content)

        self.assertEquals(file_value, '')

    def testModifyField(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Delete file field value
        new_value = 'example of content'
        file_field.set(file_content, new_value)

        # Get file value
        file_value = file_field.get(file_content)

        # Test value
        self.assertEquals(str(file_value), new_value)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'text/plain')

# #############################################################################
# UID OPERATIONS
# #############################################################################
    def test_setUID(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Modify UID
        file_content._setUID('dummyUID')
        self.assertEquals(file_content.UID(), "dummyUID")

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')



# #############################################################################
# VIRTUAL BINARY OPERATIONS
# #############################################################################
    def testVirtualBinaryAbsoluteUrl(self):

        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test absolute_url
        url = '%(instance_url)s/fss_get/%(name)s' % {
            'instance_url': file_content.absolute_url(),
            'name': 'file',
            }
        self.assertEquals(file_value.absolute_url(), url)


# #############################################################################
# Test File Stream Operator
# #############################################################################

    def _testFileStreamIterator(self,start,end):
        """
        unit test about range_filestream_iterator
        """
        # Create content
        from FSSTestCase import CONTENT_PATH

        # Create range file stream iterator
        from Products.FileSystemStorage.FileSystemStorage import \
            range_filestream_iterator

        iterator = range_filestream_iterator(CONTENT_PATH,start,end,mode='rb')
        data=''
        for i in iterator:
            data +=i
        self.assertEqual(len(data) , end - start  ,
                         '%i != %i len is not correct' % \
                                 (len(data),  end  - start))



    def testRangeFileStreamIterator(self):
        """ test range operation of file stream operator """
        #begin of the file
        self._testFileStreamIterator(0,10)
        #middle
        self._testFileStreamIterator(30,1000)
        #end

        self._testFileStreamIterator(500,1023)
        #

    def testRangeSupport(self):
        """
        functionnal test of range support
        """

        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)
        # Get file field
        file_field = file_content.getField('file')
        file_content = file_field.get(file_content)
        # do an simple request
        e = {'SERVER_NAME':'foo', 'SERVER_PORT':'80', 'REQUEST_METHOD':'GET'}
        out = StringIO()
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)
        self.failUnless(len(data) == len(file_content) ,
                        'not good lenght data ')

        # now do an range request with one range
        e =  {'SERVER_NAME':'foo',
              'SERVER_PORT':'80',
              'REQUEST_METHOD':'GET',
              'HTTP_RANGE' : 'bytes=0-10' }
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)
        read_data = ''
        for d in data:
            read_data +=d

        self.failUnless(len(read_data) == 11 ,
                        'not good lenght data <%s>' % len(read_data))

        # now mulitple range
        e =  {'SERVER_NAME':'foo',
              'SERVER_PORT':'80',
              'REQUEST_METHOD':'GET',
              'HTTP_RANGE' : 'bytes=0-10, 50-80' }
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)



# Test all content metadata
strategies = (
    ('FlatStorageStrategy', 'from Products.FileSystemStorage.strategy import FlatStorageStrategy'),
    ('DirectoryStorageStrategy', 'from Products.FileSystemStorage.strategy import DirectoryStorageStrategy'),
    ('SiteStorageStrategy', 'from Products.FileSystemStorage.strategy import SiteStorageStrategy'),
    ('SiteStorageStrategy2', 'from Products.FileSystemStorage.strategy import SiteStorageStrategy2'),
    )


dynamic_class = """
%(import)s

class Test%(name)s(TestFSS):
    "Test fss"

    strategy_klass = %(name)s
"""

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()

    module = sys.modules[TestFSS.__module__]

    # Build dynamic test cases
    for strategy in strategies:
        code = dynamic_class % {
            'name' : strategy[0],
            'import' : strategy[1],
            }

        exec code in module.__dict__
        suite.addTest(makeSuite(getattr(module, 'Test%s' % strategy[0])))

    return suite

if __name__ == '__main__':
    framework()
