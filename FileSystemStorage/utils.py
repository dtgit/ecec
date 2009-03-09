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
$Id: utils.py 43824 2007-06-15 17:08:16Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Archetypes imports
from Products.Archetypes.Field import ImageField

def getFieldValue(self, name):
    """Returns field value of an object

    @param name: Name of the field
    """

    field = self.getField(name)
    if not field:
        # Get Image fields
        # Check for scales
        found = False
        fields = [x for x in self.Schema().fields() if isinstance(x, ImageField)]
        for field in fields:
            field_name = field.getName()
            names = ['%s_%s' % (field_name, x) for x in field.getAvailableSizes(self).keys()]
            if name in names:
                obj = field.getStorage(self).get(name, self)
                found = True
                break
        if not found:
            raise AttributeError(name)
        return obj.__of__(self)

    # Standard field
    accessor = field.getAccessor(self)

    if accessor is None:
        return None

    return accessor()
