## -*- coding: utf-8 -*-
## Copyright (C) 2006-2007 Ingeniweb

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
Base test case
$Id: FSSTestCase.py 45387 2007-07-10 17:10:32Z glenfant $
"""

# Python imports
import os
import time
import Globals

# Zope imports
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import PLONE21, PLONE25

# Products imports
from Products.FileSystemStorage.config import INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE, \
     ZOPE_VERSION

if ZOPE_VERSION[:2] >= (2, 9):
    import transaction

# Globals
portal_name = 'portal'
portal_owner = 'portal_owner'
default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password

STORAGE_PATH = os.path.join(Globals.INSTANCE_HOME, 'var', 'unittests_storage')
BACKUP_PATH = os.path.join(Globals.INSTANCE_HOME, 'var', 'unittests_backup')

DATA_PATH = os.path.join(Globals.INSTANCE_HOME, 'Products', 'FileSystemStorage', 'tests', 'data')
CONTENT_PATH = os.path.join(DATA_PATH, 'word.doc')
IMAGE_PATH = os.path.join(DATA_PATH, 'image.jpg')
CONTENT_TXT = """mytestfile"""


def commit_transaction():
    # Transaction machinery depending on Zope version

    if ZOPE_VERSION[:2] >= (2, 9):
        transaction.savepoint(optimistic=True)
    else:
        get_transaction().commit(1)  
    return


class FSSTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        
        # Create temporary dirs to run test cases
        for base_path in (STORAGE_PATH, BACKUP_PATH):
            if not os.path.exists(base_path):
                os.mkdir(base_path)

        self.fss_tool = getToolByName(self.portal, 'portal_fss')
        
        # Patch getStorageStragegy to test all strategies
        strategy_klass = self.strategy_klass
        def getStorageStrategy(self):
            return strategy_klass(STORAGE_PATH, BACKUP_PATH)
        
        from Products.FileSystemStorage.FSSTool import FSSTool
        FSSTool.getStorageStrategy = getStorageStrategy
        
        # Check if fss is switched
        self.use_atct = False
        ttool = getToolByName(self.portal, 'portal_types')
        info = ttool.getTypeInfo('Folder')
        if info.getProperty('meta_type') == 'ATFolder':
            self.use_atct = True
        
    def beforeTearDown(self):
        """Remove all the stuff again.
        """

        import shutil
        shutil.rmtree(STORAGE_PATH)
        shutil.rmtree(BACKUP_PATH)
        return

    def getDataPath(self):
        """Returns data path used for test cases"""
    
        return DATA_PATH
    
    def loginAsPortalOwner(self):
        '''Use if you need to manipulate an article as member.'''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)

    def addFileByString(self, folder, content_id):
        """Adds a file by string.
        """
        
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        commit_transaction()
        kw = {'file' : CONTENT_TXT}
        content.edit(**kw)
        return content

    def addFileByFileUpload(self, folder, content_id):
        """Adds a file by file upload.
        """
        
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        commit_transaction()
        self.updateContent(content, 'file', CONTENT_PATH)
        return content
        
    def addImageByFileUpload(self, folder, content_id):
        """
        Adding image
        """
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        commit_transaction()
        self.updateContent(content, 'image', IMAGE_PATH)
        return content

    def updateContent(self, content, field, filepath):
        """Updates a field content for a file.
        """
        
        from dummy import FileUpload
        file = open(filepath, 'rb')
        file.seek(0)
        filename = filepath.split('/')[-1]
        fu = FileUpload(filename=filename, file=file)
        kw = {field: fu}
        content.edit(**kw)

DEFAULT_PRODUCTS = ['kupu', 'FileSystemStorage']

# We need Five (zope 2.8) and require kupu under plone 2.1
if PLONE21 and not PLONE25:
    ZopeTestCase.installProduct('Five')
    ZopeTestCase.installProduct('kupu')

# On Plone 2.0, install AT1.3
if not PLONE21 and not PLONE25:
    ZopeTestCase.installProduct('kupu')
    ZopeTestCase.installProduct('Archetypes')
    ZopeTestCase.installProduct('PortalTransforms')
    ZopeTestCase.installProduct('MimetypesRegistry')
    DEFAULT_PRODUCTS = ['ATContentTypes', 'kupu', 'FileSystemStorage']

# Install FSS Example types
os.environ[INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE] = 'True' 
## ZopeTestCase.installProduct('PortalTransforms')
## ZopeTestCase.installProduct('MimetypesRegistry')
## ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('FileSystemStorage')

HAS_ATCT = True
ZopeTestCase.installProduct('ATContentTypes')

# Setup Plone site   
PloneTestCase.setupPloneSite(products=DEFAULT_PRODUCTS)
