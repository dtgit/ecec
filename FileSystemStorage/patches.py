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
"""Patch __bobo_traverse__ method of BaseObject in AT product

Make the following example works
Example :
You have an ATobject in ZODB at /mysite/myobject
This object has an ImageField (image) using FSS
Doing /mysite/myobject/image should get the image
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: patches.py 43824 2007-06-15 17:08:16Z glenfant $
__docformat__ = 'restructuredtext'


# Check for Plone 2.5 or above
try:
    from Products.CMFPlone.migrations import v2_5
except ImportError:
    PLONE25 = False
else:
    PLONE25 = True

# For plone 2.5 we have registered  an ITraversal adapter for BaseObject
FSS_BOBO_PATCH = PLONE25

if not FSS_BOBO_PATCH:

    from Products.FileSystemStorage.utils import getFieldValue       
    def new_bobo_traverse(self, REQUEST, name):
        """Access to field values that are not using AttributeStorage
        """
        try:
            return self._fss_old_bobo_traverse(REQUEST, name)
        except AttributeError:
            return getFieldValue(self, name)

    from Products.Archetypes.atapi import BaseObject

    BaseObject._fss_old_bobo_traverse = BaseObject.__bobo_traverse__       
    BaseObject.__bobo_traverse__ = new_bobo_traverse

    FSS_BOBO_PATCH = True