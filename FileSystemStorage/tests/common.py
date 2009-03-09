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
Common resources for tests
$Id: common.py 43824 2007-06-15 17:08:16Z glenfant $
"""

# Python imports
import random
import os
import sys
from types import StringType

# Zope imports
from Testing import ZopeTestCase
from OFS.Image import File

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.PloneTestCase.setup import PLONE21, PLONE25

# Archetypes imports
from Products.Archetypes.interfaces.base import IBaseUnit

# Products imports
from Products.FileSystemStorage.tests import FSSTestCase
from Products.FileSystemStorage.FileSystemStorage import VirtualBinary

FOLDER_TYPE = "Folder"

# On Plone 2.0, use ATFolder
if not PLONE21 and not PLONE25:
    FOLDER_TYPE = "ATFolder"

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
