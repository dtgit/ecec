# -*- coding: utf-8 -*-
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
The FileSystemStorage package
$Id: __init__.py 45387 2007-07-10 17:10:32Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
import os
import sys
from Globals import package_home

# CMF imports
from Products.CMFCore.utils import ContentInit, ToolInit
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory

# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# Products imports
from Products.FileSystemStorage.config import \
    SKINS_DIR, \
    GLOBALS, \
    PROJECTNAME, \
    DEBUG, \
    INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE, \
    PLONE_VERSION


from Products.FileSystemStorage import patches

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    install_types = DEBUG or \
        os.environ.get(INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE)
    
    if install_types:
        # Import example types
        from Products.FileSystemStorage.examples import FSSItem
    
        content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                          PROJECTNAME)
        ContentInit('%s Content' % PROJECTNAME,
                    content_types = content_types,
                    permission = CMFCorePermissions.AddPortalContent,
                    extra_constructors = constructors,
                    fti = ftis,
                    ).initialize(context)
    
    # Import tool
    from Products.FileSystemStorage.FSSTool import FSSTool
    
    ToolInit(
        '%s Tool' % PROJECTNAME,
        tools=(FSSTool,),
        product_name=PROJECTNAME,
        icon='tool.gif').initialize(context)
