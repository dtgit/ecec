# -*- coding: utf-8 -*-
## FileSystemStorage
## Copyright (C)2006 Ingeniweb

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
The FileSystemStorage tool
$Id: FSSTool.py 44602 2007-06-26 14:02:03Z davconvent $
"""

__version__ = "$Revision$"
__docformat__ = 'restructuredtext'


# Python imports
import os
import re
import random
import time
import Globals

# Zope imports
from Globals import package_home
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from DateTime import DateTime
from ZPublisher.Iterators import IStreamIterator
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression

# Products imports
from FileUtils import rm_file
from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
from Products.FileSystemStorage.utils import getFieldValue
from Products.FileSystemStorage.config import ZCONFIG, CONFIG_FILE
from Products.FileSystemStorage import strategy as fss_strategy

_zmi = os.path.join(os.path.dirname(__file__), 'zmi')

# {storage-strategy (from config file): strategy class, ...}
_strategy_map = {
    'flat': fss_strategy.FlatStorageStrategy,
    'directory': fss_strategy.DirectoryStorageStrategy,
    'site1': fss_strategy.SiteStorageStrategy,
    'site2': fss_strategy.SiteStorageStrategy2
    }

class FSSTool(PropertyManager, UniqueObject, SimpleItem, ActionProviderBase):
    """Tool for FileSystem storage"""

    plone_tool = 1
    id = 'portal_fss'
    title = 'FileSystemStorage tool'
    rdf_enabled = False
    rdf_script = ''
    meta_type = 'FSSTool'

    _properties=(
        {'id':'title', 'type': 'string', 'mode':'w'},
        {'id':'rdf_enabled', 'type': 'boolean', 'mode':'w'},
        {'id':'rdf_script', 'type': 'string', 'mode':'w'},
        )

    _actions = ()

    manage_options = (
        ({'label': 'Overview',
          'action': 'manage_overview'
          },
         {'label': 'Documentation',
          'action': 'manage_documentation'
          }) +
        ActionProviderBase.manage_options +
        PropertyManager.manage_options +
        SimpleItem.manage_options)

    security = ClassSecurityInfo()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        self.initProperties()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'initProperties')
    def initProperties(self):
        """Init properties"""

        default_path = os.path.join(Globals.INSTANCE_HOME, 'var')
        self.storage_path = default_path
        self.backup_path = default_path

    security.declareProtected(CMFCorePermissions.View, 'isRDFEnabled')
    def isRDFEnabled(self):
        """Returns true if RDF is automaticaly generated when file added"""

        return self.rdf_enabled

    security.declareProtected(CMFCorePermissions.ManagePortal, 'enableRDF')
    def enableRDF(self, enabled):
        """Enable rdf or not"""

        if enabled:
            self.rdf_enabled = True
        else:
            self.rdf_enabled = False

    security.declareProtected(CMFCorePermissions.View, 'getRDFScript')
    def getRDFScript(self):
        """Returns rdf script used to generate RDF on files"""

        return self.rdf_script

    security.declareProtected(CMFCorePermissions.ManagePortal, 'setRDFScript')
    def setRDFScript(self, rdf_script):
        """Set rdf script used to generate RDF on files"""

        self.rdf_script = rdf_script


    def getStorageStrategy(self):
        """Returns the storage strategy"""

        global _strategy_map
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())
        strategy_class = _strategy_map[ZCONFIG.storageStrategyForSite(portal_path)]
        return strategy_class(
            ZCONFIG.storagePathForSite(portal_path),
            ZCONFIG.backupPathForSite(portal_path))


    security.declareProtected(CMFCorePermissions.ManagePortal, 'getUIDToPathDictionnary')
    def getUIDToPathDictionnary(self):
        """Returns a dictionnary

        For one uid (key) give the correct path (value)
        """

        ctool = getToolByName(self, 'uid_catalog')
        brains = ctool(REQUEST={})
        return dict([(x['UID'], x.getPath()) for x in brains])

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getPathToUIDDictionnary')
    def getPathToUIDDictionnary(self):
        """Returns a dictionnary

        For one path (key) give the correct UID (value)
        """

        ctool = getToolByName(self, 'uid_catalog')
        brains = ctool(REQUEST={})
        return dict([(x.getPath(), x['UID']) for x in brains])

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getFSSBrains')
    def getFSSBrains(self, items):
        """Returns a dictionnary.

        For one uid, returns a dictionnary containing of fss item stored on
        filesystem:
        - uid: UID of content
        - path: Path of content
        - name: Name of field stored on filesystem
        - size: Size in octets of field value stored on filesystem
        - fs_path: Path on filesystem where the field value is stored
        """

        if not items:
            return []

        # Get the first item of items list and check if item has uid or path key
        if not items[0].has_key('uid'):
            # Use path to uid dictionnary
            path_to_uid = self.getPathToUIDDictionnary()
            for item in items:
                item['uid'] = path_to_uid.get(item['path'], None)
        else:
            # Use uid to path dictionnary
            uid_to_path = self.getUIDToPathDictionnary()
            for item in items:
                item['path'] = uid_to_path.get(item['uid'], None)

        return items


    security.declareProtected(CMFCorePermissions.ManagePortal, 'getStorageBrains')
    def getStorageBrains(self):
        """Returns a list of brains in storage path"""

        strategy = self.getStorageStrategy()
        items = strategy.walkOnStorageDirectory()
        return self.getFSSBrains(items)


    security.declareProtected(CMFCorePermissions.ManagePortal, 'getStorageBrainsByUID')
    def getStorageBrainsByUID(self, uid):
        """ Returns a list containing all brains related to fields stored
        on filesystem of object having the specified uid"""

        return [x for x in self.getStorageBrains() if x['uid'] == uid]

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getBackupBrains')
    def getBackupBrains(self):
        """Returns a list of brains in backup path"""

        strategy = self.getStorageStrategy()
        items = strategy.walkOnBackupDirectory()
        return self.getFSSBrains(items)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getFSStats')
    def getFSStats(self):
        """
        Returns stats on FileSystem storage
        valid_files_count -> Count of valid files
        not_valid_files_count -> Count of not valid files
        valid_backups_count -> Count of valid backups
        not_valid_backups_count -> Count of not valid backups
        """

        storage_brains = self.getStorageBrains()
        backup_brains = self.getBackupBrains()

        valid_files = [x for x in storage_brains if x['path'] is not None]
        not_valid_files = [x for x in storage_brains if x['path'] is None]
        valid_backups = [x for x in backup_brains if x['path'] is None]
        not_valid_backups = [x for x in backup_brains if x['path'] is not None]


        # Sort valid files by size
        def cmp_size(a, b):
              return cmp(a['size'], b['size'])

        valid_files.sort(cmp_size)

        # Size in octets
        total_size = 0
        largest_size = 0
        smallest_size = 0
        average_size = 0

        for x in valid_files:
            total_size += x['size']

        if len(valid_files) > 0:
            largest_size = valid_files[-1]['size']
            smallest_size = valid_files[0]['size']
            average_size = int(total_size / len(valid_files))

        stats = {
          'valid_files_count' : len(valid_files),
          'not_valid_files_count' : len(not_valid_files),
          'valid_backups_count' : len(valid_backups),
          'not_valid_backups_count' : len(not_valid_backups),
          'total_size' : total_size,
          'largest_size': largest_size,
          'smallest_size' : smallest_size,
          'average_size' : average_size,
          }

        return stats

    security.declareProtected(CMFCorePermissions.ManagePortal, 'updateFSS')
    def updateFSS(self):
        """
        Update FileSystem storage
        """

        storage_brains = self.getStorageBrains()
        backup_brains = self.getBackupBrains()

        not_valid_files = tuple([x for x in storage_brains if x['path'] is None])
        not_valid_backups = tuple([x for x in backup_brains if x['path'] is not None])
        strategy = self.getStorageStrategy()

        # Move not valid files in backup
        for item in not_valid_files:
            strategy.unsetValueFile(**item)

        # Move not valid backups in file storage
        for item in not_valid_backups:
            strategy.restoreValueFile(**item)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'removeBackups')
    def removeBackups(self, max_days):
        """
        Remove backups older than specified days
        """

        backup_brains = self.getBackupBrains()
        valid_backups = [x for x in backup_brains if x['path'] is None]
        current_time = time.time()

        for item in valid_backups:
            one_day = 86400 # One day 86400 seconds
            modified = item['modified']
            seconds = int(current_time) - int(modified.timeTime())
            days = int(seconds/one_day)

            if days >= max_days:
                rm_file(item['fs_path'])

    security.declareProtected(CMFCorePermissions.ManagePortal, 'updateRDF')
    def updateRDF(self):
        """Add RDF files to fss files"""

        rdf_script = self.getRDFScript()
        storage_brains = self.getStorageBrains()
        strategy = self.getStorageStrategy()

        for item in storage_brains:
            instance_path = item['path']
            if instance_path is None:
                continue

            try:
                instance = self.restrictedTraverse(instance_path)
            except AttributeError:
                # The object doesn't exist anymore, we continue
                continue
            name = item['name']
            field = instance.getField(name)
            if field is None:
                continue
            storage = field.getStorage(instance)
            if not isinstance(storage, FileSystemStorage):
                continue

            # Get FSS info
            info = storage.getFSSInfo(name, instance)
            if info is None:
                continue

            # Call the storage strategy
            rdf_value = info.getRDFValue(name, instance, rdf_script=rdf_script)
            strategy.setRDFFile(rdf_value, uid=item['uid'], name=name)

    def getFSSItem(self, instance, name):
        """Get value of fss item.
        This method is called from fss_get script.

        @param instance: Object containing FSS item
        @param name: Name of FSS item to get
        """

        return getFieldValue(instance, name)

    ###
    ## ZMI/PMI helpers (making a Zope 3 style view would be overkill)
    ###

    security.declareProtected(CMFCorePermissions.ManagePortal, 'siteConfigInfo')
    def siteConfigInfo(self):
        """A TALES friendly configuration info mapping for this Plone site"""

        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())
        return {
            'config_file': CONFIG_FILE,
            'strategy': ZCONFIG.storageStrategyForSite(portal_path),
            'storage_path': ZCONFIG.storagePathForSite(portal_path),
            'backup_path': ZCONFIG.backupPathForSite(portal_path)
            }

    security.declareProtected(CMFCorePermissions.ManagePortal, 'globalConfigInfo')
    def globalConfigInfo(self):
        """A TALES friendly configuration info mapping for global configuration"""

        return {
            'config_file': CONFIG_FILE,
            'strategy': ZCONFIG.storageStrategyForSite('/'),
            'storage_path': ZCONFIG.storagePathForSite('/'),
            'backup_path': ZCONFIG.backupPathForSite('/')
            }


    security.declareProtected(CMFCorePermissions.ManagePortal, 'formattedReadme')
    def formattedReadme(self):
        """README.txt (reStructuredText) transformed to HTML"""

        from reStructuredText import HTML
        readme_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.txt')
        return HTML(file(readme_path).read(), report_level=100) # No errors/warnings -> faster

    ###
    ## ZMI views
    ###
    
    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('manage_overview', _zmi)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_documentation')
    manage_documentation = PageTemplateFile('manage_documentation', _zmi)

InitializeClass(FSSTool)
