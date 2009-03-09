##################################################################################
#
#    Copyright (C) 2006 Utah State University, All rights reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.interface import implements
from zope.component import adapts
from Products.eduCommons.interfaces import IClearCopyrightable, IClearCopyright, IAccessibilityCompliant, IAccessibilityCompliantable
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import  PersistentMapping

CCKEY = 'eduCommons.clearcopyright'
ACCESSIBLEKEY = 'eduCommons.accessible'

class ClearCopyright(object):
    """
        This class adds a clear copyright fields to content
    """
    adapts(IClearCopyrightable)
    implements(IClearCopyright)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)

        mapping = self.annotations.get(CCKEY)
        mapping = self.annotations.get(CCKEY)
        if mapping is None:
            clearcopyright = False
            mapping = self.annotations[CCKEY] = clearcopyright = PersistentMapping()
            self.mapping = mapping
        else:
            self.mapping = mapping

    def getClearedCopyright(self):
        """ Get the contents of the clear copyright field. """
        return self.annotations[CCKEY]

    def setClearedCopyright(self, ccdata):
        """ Set the clear copyright field. """
        self.annotations[CCKEY] = ccdata

    clearedcopyright = property(fget=getClearedCopyright, fset=setClearedCopyright)

class AccessibilityCompliant(object):
    """
        This class adds an Accessibility Compliance field to content
    """
    adapts(IAccessibilityCompliantable)
    implements(IAccessibilityCompliant)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)

        mapping = self.annotations.get(ACCESSIBLEKEY)
        mapping = self.annotations.get(ACCESSIBLEKEY)
        if mapping is None:
            accessible = False
            mapping = self.annotations[ACCESSIBLEKEY] = accessible = PersistentMapping()
            self.mapping = mapping
        else:
            self.mapping = mapping

    def getAccessibilityCompliant(self):
        """ Get the contents of the accessibility field. """
        return self.annotations[ACCESSIBLEKEY]

    def setAccessibilityCompliant(self, accessibledata):
        """ Set the accessible field. """
        self.annotations[ACCESIBLEKEY] = accessibledata

    accessibilitycompliant = property(fget=getAccessibilityCompliant, fset=setAccessibilityCompliant)

