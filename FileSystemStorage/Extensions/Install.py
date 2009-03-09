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
Resources for CMF quick installer
$Id: Install.py 43824 2007-06-15 17:08:16Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
from StringIO import StringIO
import string

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes.public import listTypes

# Products imports
from Products.FileSystemStorage.config import PROJECTNAME, GLOBALS, fss_prefs_configlet
from Products.FileSystemStorage.FSSTool import FSSTool

def install(self):
    out = StringIO()

    # Install types
    type_info = listTypes(PROJECTNAME)
    installTypes(self, out, type_info, PROJECTNAME)

    # Install tools
    add_tool = self.manage_addProduct[PROJECTNAME].manage_addTool
    if not self.objectIds(spec=FSSTool.meta_type):
        add_tool(FSSTool.meta_type)

    # Install skin
    install_subskin(self, out, GLOBALS)

    # Install configlet
    cp_tool = getToolByName(self, 'portal_controlpanel')
    try:
        cp_tool.registerConfiglet(**fss_prefs_configlet)
    except:
        pass

    out.write('Installation completed.\n')
    return out.getvalue()

def uninstall(self):
    out = StringIO()

    # Uninstall configlets
    try:
        cp_tool = getToolByName(self, 'portal_controlpanel')
        cp_tool.unregisterApplication(PROJECTNAME)
    except:
        pass

    out.write('Uninstallation completed.\n')
    return out.getvalue()
