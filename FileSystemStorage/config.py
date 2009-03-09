# -*- coding: utf-8 -*-
## Copyright (C) 2006 - 2007 Ingeniweb

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
Global FileSystemStorage configuration data
$Id: config.py 47875 2007-08-23 15:37:24Z encolpe $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# CMF imports
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions

PROJECTNAME = 'FileSystemStorage'
GLOBALS = globals()
SKINS_DIR = 'skins'
DEBUG = False
INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE = 'FSS_INSTALL_EXAMPLE_TYPES'

from App.version_txt import getZopeVersion
ZOPE_VERSION = getZopeVersion() # = (2, 9, 5, ...)
del getZopeVersion

try:
    from Products.CMFPlone.utils import getFSVersionTuple
    PLONE_VERSION = getFSVersionTuple()[:2] # as (2, 1)
    del getFSVersionTuple
except ImportError, e:
    PLONE_VERSION = (2, 0)

ZCONFIG, dummy_handler, CONFIG_FILE = None, None, None

def loadConfig():
    """Loads configuration from a ZConfig file"""

    global ZCONFIG, dummy_handler, CONFIG_FILE

    import os
    from Globals import INSTANCE_HOME
    from ZConfig.loader import ConfigLoader
    from Products.FileSystemStorage.configuration.schema import fssSchema

    # Configuration directories
    INSTANCE_ETC = os.path.join(INSTANCE_HOME, 'etc')
    _this_directory = os.path.abspath(os.path.dirname(__file__))
    FSS_ETC = os.path.join(_this_directory, 'etc')

    def filePathOrNone(file_path):
        return os.path.isfile(file_path) and file_path or None
    
    # (Potential) configuration files
    CONFIG_FILENAME = 'plone-filesystemstorage.conf'
    INSTANCE_CONFIG = filePathOrNone(os.path.join(INSTANCE_ETC, CONFIG_FILENAME))
    FSS_CONFIG = filePathOrNone(os.path.join(FSS_ETC, CONFIG_FILENAME))
    FSS_CONFIG_IN = filePathOrNone(os.path.join(FSS_ETC, CONFIG_FILENAME + '.in'))

    # We configure on the first available config file
    CONFIG_FILE = [fp for fp in (INSTANCE_CONFIG, FSS_CONFIG, FSS_CONFIG_IN)
                   if fp is not None][0]

    # We ignore personal configuration on unit tests
    if os.environ.has_key('ZOPE_TESTCASE'):
        ZCONFIG, dummy_handler = ConfigLoader(fssSchema).loadURL(FSS_CONFIG_IN)
    else:
        ZCONFIG, dummy_handler = ConfigLoader(fssSchema).loadURL(CONFIG_FILE)


    # Dirty but we need to reinit datatypes control globals since this
    # initialisation seems to be called more than once with Zope 2.8
    # (why ???)
    from Products.FileSystemStorage.configuration import datatypes
    datatypes._paths = []
    return

loadConfig()
del loadConfig

# Configlets
fss_prefs_configlet = {
    'id': 'fss_prefs',
    'appId': PROJECTNAME,
    'name': 'FileSystem storage Preferences',
    'action': 'string:$portal_url/fss_management_form',
    'category': 'Products',
    'permission': (CMFCorePermissions.ManagePortal,),
    'imageUrl': 'fss_tool.gif',
    }
