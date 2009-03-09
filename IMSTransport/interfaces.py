##################################################################################
#
#    Copyright (C) 2004-2006 Utah State University, All rights reserved.
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

__author__ = '''Brent Lambert, David Ray, Jon Thomas'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.interface import Interface
from zope.component.interfaces import IObjectEvent


class IIMSManifestWriter(Interface):
    """ Write an IMS Content Package manifest document. """

    def setWriterType(wtype):
        """ Set the writer type, which determines how objects are written,
            and which event handler writes them. """

    def setDestination(dest):
        """ Set the destination for data written by the manifest writer. """

    def writeManifest():
        """ Write the manifest. """

    def getManifest():
        """ Get the manifest expressed in XML. """

class IIMSManifestReader(Interface):
    """ Read an IMS Content Package manifest document. """

    def setReaderType(rtype):
        """ Set the reader type, which determines how objects are created,
            and which event handler creates them. """

    def setSource(source):
        """ Set the source of the data used by the manifest reader. """

    def setRequiredMetadataSections(sections):
        """ Set which metadata sections should be required. Useful if you
            want to define your own metadata section, and have it be required. """

    def readManifest(manifest):
        """ Read a manifest """

class ISetNameSpaces(IObjectEvent):
    """ Set namespace information in manifest. """
    
class IObjectWriteMetadata(IObjectEvent):
    """ Write LOM Metadata event """
    
class IObjectReadMetadata(IObjectEvent):
    """ Write LOM Metadata event """
    
class IObjectWriteOrganizations(IObjectEvent):
    """ Write and organization entry """
    
class IObjectReadOrganizations(IObjectEvent):
    """ Write and organization entry """

class IObjectWriteContributeNode(IObjectEvent):
    """ Write contribute node event """

class IObjectReadContributeNode(IObjectEvent):
    """ Read contribute node event """
    
class IObjectCreateObject(IObjectEvent):
    """ Create an object from manifest data. """
    
class IObjectTransformPackage(IObjectEvent):
    """ Transform IMS package into a format we can consume. """

