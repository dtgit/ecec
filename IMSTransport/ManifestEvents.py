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


from zope.component.interfaces import ObjectEvent
from zope.interface import implements
from interfaces import ISetNameSpaces, IObjectWriteMetadata, IObjectReadMetadata, \
                       IObjectWriteOrganizations, IObjectReadOrganizations, \
                       IObjectWriteContributeNode, IObjectReadContributeNode, \
                       IObjectCreateObject, IObjectTransformPackage


class SetNameSpaces(ObjectEvent):
    """ Set namespace information in manifest. """
    implements(ISetNameSpaces)

    def __init__(self, object, writer):
        super(SetNameSpaces, self).__init__(object)
        self.writer = writer

class ObjectWriteMetadata(ObjectEvent):
    """ Write metadata to content package. """
    implements(IObjectWriteMetadata)

    def __init__(self, object, node, writer):
        super(ObjectWriteMetadata, self).__init__(object)
        self.node = node
        self.writer = writer

        
class ObjectReadMetadata(ObjectEvent):
    """ Read metadata from content package. """
    implements(IObjectReadMetadata)

    def __init__(self, object, metadata, node, reader, mdSections, resid):
        super(ObjectReadMetadata, self).__init__(object)
        self.metadata = metadata
        self.node = node
        self.reader = reader
        self.mdSections = mdSections
        self.resid = resid

        
class ObjectWriteOrganizations(ObjectEvent):
    """ Write Organizations entries. """
    implements (IObjectWriteOrganizations)
    
    def __init__(self, object, node, writer):
        super(ObjectWriteOrganizations, self).__init__(object)
        self.node = node
        self.writer = writer

        
class ObjectReadOrganizations(ObjectEvent):
    """ Read Organization entries. """
    implements (IObjectReadOrganizations)
    
    def __init__(self, object, node, reader, org):
        super(ObjectReadOrganizations, self).__init__(object)
        self.node = node
        self.reader = reader
        self.org = org

        
class ObjectWriteContributeNode(ObjectEvent):
    """ Write a contribute entry. """
    implements(IObjectWriteContributeNode)

    def __init__(self, object, node, writer, mwriter):
        super(ObjectWriteContributeNode, self).__init__(object)
        self.node = node
        self.writer = writer
        self.mwriter = mwriter


class ObjectReadContributeNode(ObjectEvent):
    """ Read a contribute entry. """
    implements(IObjectReadContributeNode)

    def __init__(self, object, metadata, source, value, vlist, date):
        super(ObjectReadContributeNode, self).__init__(object)
        self.metadata = metadata
        self.source = source
        self.value = value
        self.vlist = vlist
        self.date = date


class ObjectCreateObject(ObjectEvent):
    """ Creates an object from manifest data. """
    implements(IObjectCreateObject)

    def __init__(self, object, rtype, resource, data, metadata):
        super(ObjectCreateObject, self).__init__(object)
        self.rtype = rtype
        self.resource = resource
        self.data = data
        self.metadata = metadata
        

class ObjectTransformPackage(ObjectEvent):
    """ Transform an IMS package to a format we can consume. """
    implements(IObjectTransformPackage)

    def __init__(self, context, manifest, package_type, xformdata):
        super(ObjectTransformPackage, self).__init__(object)
        self.context = context
        self.manifest = manifest
        self.package_type = package_type
        self.xformdata = xformdata
