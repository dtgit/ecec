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
The storage definition
$Id: FileSystemStorage.py 54530 2007-11-27 09:22:03Z yboussard $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
import os
import Globals
from Acquisition import aq_base
from StringIO import StringIO
from types import StringType, UnicodeType
from new import instancemethod

# Zope imports
from webdav.common import rfc1123_date
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Image import File
from OFS.SimpleItem import SimpleItem
from ZPublisher.Iterators import filestream_iterator
#from Shared.DC.ZRDB.TM import TM

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.Storage import StorageLayer
from Products.Archetypes.interfaces.field import IObjectField, IImageField
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.Field import ImageField
try:
    from Products.Archetypes.Field import Image # Changes since AT1.3.4
except:
    from OFS.Image import Image

# Products imports
from Products.FileSystemStorage.rdf import RDFWriter
from FileUtils import copy_file, move_file, rm_file

from ZPublisher.Iterators import IStreamIterator
from ZPublisher.HTTPRangeSupport import parseRange

class range_filestream_iterator(file):
    """
    a file subclass which implements an iterator that returns a
    fixed-sized sequence of bytes.
    this filestream iterator return only file portion specify by
    http range header
    A range header is send by client when he wants a portion file

    the request looks like

    GET /file.pdf HTTP/1.1
    Range: bytes=0-10
    Host: host

    And the response must have range of bit specified by the range header

    HTTP/1.1 206 Partial Content
    Accept-Ranges: bytes
    Content-Length: 11
    Content-Range: bytes 0-10/1362006
    Content-Type: application/pdf

    PDF%1.6

    The default filestream_iterator does not support this range

    """

    __implements__ = (IStreamIterator,)

    def __init__(self, name, start, end,mode='r', bufsize=-1, streamsize=1<<16):
        """
        @param :
        name  : file name in filesystem
        start : begin of the range
        end   : end of the range
        """
        self.end = end
        file.__init__(self, name, mode, bufsize)
        self.seek(start, 0)
        self.streamsize = streamsize


    def next(self):
        """
        raise a stopIteration if read bytes is upper than end value specified
        by the range validator
        """

        if self.tell() >= self.end:
            ## nothing to read
            raise StopIteration

        if self.tell() + self.streamsize > self.end:
            ## case of we must stop to the end buffer
            data = self.read(self.end - self.tell())
            if not data:
                raise StopIteration
            return data

        else:
            ## normaly do the job like filestream_iterator
            data = self.read(self.streamsize)
            if not data:
                raise StopIteration
            return data



    def __len__(self):
        """
        return len of the file
        """

        cur_pos = self.tell()
        self.seek(0, 2)
        size = self.tell()
        self.seek(cur_pos, 0)

        return size





class VirtualData:
    """
    Base abstract class for data stored on filesystem.
    Subclasses must have a docstring if they are to be published (like images)
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, name, instance, path):
        self.name = name
        self.instance = instance
        self.path = path
        self.__name__ = name

    def getData(self):
        """
            Returns data (as a string) stored on filesystem.
        """

        # Use StringIO for large files
        virtual_file = StringIO()
        value = ''

        # Make sure file exists. If not returns empty string
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            return ''

        # Copy all data in one pass
        try:
            copy_file(self.path, virtual_file)
            virtual_file.seek(0)
            value = virtual_file.getvalue()
        finally:
            virtual_file.close()

        return value

    def __str__(self):
        return str(self.getData())

    def __len__(self):
        return len(str(self))

    def __getattr__(self, key):
        if key == 'data':
            return self.getData()

    read = __str__

InitializeClass(VirtualData)

class VirtualBinary(VirtualData):
    """
    Base class for binary data
    """

    __content_class__ = None

    def __init__(self, name, instance, path, filename, mimetype, size):
        VirtualData.__init__(self, name, instance, path)
        self.filename = filename
        self.content_type = mimetype
        self.size = size

    def __len__(self):
        return self.size

    def absolute_url(self):
        url = '%(instance_url)s/fss_get/%(name)s' % {
            'instance_url': self.instance.absolute_url(),
            'name': self.name,
            }

        return url

    def index_html(self, REQUEST, RESPONSE=None):
        """Default view for VirtualBinary file"""
        ranges = None
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        if self.__content_class__ is None:
            # Build your own headers
            RESPONSE.setHeader('Content-Type', self.content_type)
            RESPONSE.setHeader('Content-Length', self.size)

        else:
            # Call index_html method of content class with a fake
            # self.data attribute which will return empty value
            # Use this artifice to make sure content class is not loading
            # all data in memory since it is better to return a stream iterator
            # There is an exception with multiple range
            if REQUEST.environ.has_key('HTTP_RANGE'):
                ranges = parseRange(REQUEST.environ.get('HTTP_RANGE'))
             ## in case of mutiple range we don't know do with an iterator
            if ranges is not None and len(ranges) > 1:
                ## call normally OFS.image with data
                return self.__content_class__.index_html(self, REQUEST, RESPONSE)
            else:
                ## call OFS.image with no data
                setattr(self, 'data', '')
                self.__content_class__.index_html(self, REQUEST, RESPONSE)
                delattr(self, 'data')

            # This is a default header that can be bypassed by other products
            # such as attachment field.
            if RESPONSE.getHeader('content-disposition') is None: # headers are in lower case in HTTPResponse
                RESPONSE.setHeader(
                    'Content-Disposition',
                    'inline; filename="%s"' % self.filename
                    )
        if ranges and len(ranges) == 1:
            ## is an range request with one range , return an iterator with this range
            [(start,end)] = ranges
            iterator = range_filestream_iterator(self.path,start, end,  mode='rb')
            return iterator
        else:
            return filestream_iterator(self.path, mode='rb')

    def download(self, REQUEST, RESPONSE=None):
        """Download file as an attachment"""

        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        value = self.index_html(REQUEST, RESPONSE)

        # Change Content-Disposition header
        RESPONSE.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % self.filename
        )
        return value

    def get_size(self):
        return len(self)

    def getContentType(self):
        return self.content_type

    def evalCmd(self, cmd_name):
        """Eval command on storage"""

        if cmd_name not in dir(self):
            raise AttributeError, 'Unknown attribute: %s' % cmd_name

        request = self.REQUEST
        response = request.RESPONSE
        kwargs = dict(request.form)
        kwargs['REQUEST'] = request
        kwargs['RESPONSE'] = response
        cmd = getattr(self, cmd_name)
        return cmd(**kwargs)

InitializeClass(VirtualBinary)


class VirtualFile(VirtualBinary, File):
    """
    For files.
    """

    __content_class__ = File
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, name, instance, path, filename, mimetype, size):
        VirtualBinary.__init__(self, name, instance, path, filename, mimetype, size)

    def __getattr__(self, key):
        if key == 'data':
            return self.getData()
        ### useless since __getattr__ is only called when no attribute is found
        ### in this class but also in parent classes. So if we are here, neither
        ### VirtualFile nor VirtualBinary and File have the requested attribute
        ### Moreover, File class has no __getattr__ method...
        # return File.__getattr__(self, key)
        raise AttributeError(key)

InitializeClass(VirtualFile)

class VirtualImage(VirtualBinary, Image):
    """
    Image objects can be GIF, PNG or JPEG and have the same methods
    as File objects. Images also have a string representation that
    renders an HTML 'IMG' tag.
    """

    __content_class__ = Image
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, name, instance, path, filename, mimetype, size, width, height):
        VirtualBinary.__init__(self, name, instance, path, filename, mimetype, size)
        self.width = width
        self.height = height

    def __getattr__(self, key):
        if key == 'data':
            return self.getData()
        return Image.__getattr__(self, key)

InitializeClass(VirtualImage)


# ####
# Storage info
# ####

class FSSInfo(SimpleItem):
    """FileSystemStorageInfo Base class. Used for string data"""

    security = ClassSecurityInfo()

    def __init__(self, uid):
        self.update(uid)

    security.declarePrivate('update')
    def update(self, uid):
        self.uid = uid

    security.declarePrivate('getUID')
    def getUID(self):
        return self.uid

    security.declarePrivate('setUID')
    def setUID(self, uid):
        self.uid = uid

    security.declarePrivate('getValue')
    def getValue(self, name, instance, path):
        return str(VirtualData(name, instance, path))

    security.declarePrivate('getRDFFieldProperties')
    def getRDFFieldProperties(self, name, instance):
        """Returns RDF field properties list.

        Each property is defined in a dictionnary {'id': ...,  'value': ...}

        @param name: name of the field
        @param instance: Content using this storage"""

        props = (
            {'id': 'dc:title', 'value': instance.title_or_id()},
            {'id': 'dc:description', 'value': instance.Description()},
            {'id': 'dc:language', 'value': instance.Language()},
            {'id': 'dc:creator', 'value': instance.Creator()},
            {'id': 'dc:date', 'value': instance.modified()},
            {'id': 'dc:format', 'value': getattr(self, 'mimetype', 'text/plain')},
            )
        return props

    security.declarePrivate('getProperties')
    def getProperties(self):
        """Returns info attributes in a dictionnary"""

        props = {}
        props['uid'] = self.uid
        return props

    security.declarePrivate('getRDF')
    def getRDF(self, name, instance):
        """Returns RDF dictionnary to inject into RDFWriter

        @param name: name of the field
        @param instance: Content using this storage"""

        rdf_args = {}

        # Get charset
        ptool = getToolByName(instance, 'portal_properties')
        rdf_args['charset'] = ptool.site_properties.default_charset

        # Get namespaces
        rdf_args['namespaces'] = (
            {'id': 'xmlns:rdf', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
            {'id': 'xmlns:dc', 'value': 'http://purl.org/dc/elements/1.1/'},
            {'id': 'xmlns:fss', 'value': 'http://namespace.ingeniweb.com/fss'},)

        # Get field url
        utool = getToolByName(instance, 'portal_url')
        portal_path = utool.getPortalObject().getPhysicalPath()
        portal_path_len = len(portal_path)
        rel_path = '/'.join(instance.getPhysicalPath()[portal_path_len:])
        fss_path = '%s/fss_get/%s' % (rel_path, name)
        rdf_args['field_url'] = fss_path

        # Get field properties
        rdf_args['field_props'] = self.getRDFFieldProperties(name, instance)
        return rdf_args

    security.declarePrivate('getRDFValue')
    def getRDFValue(self, name, instance, rdf_script=''):
        """Returns RDF value of file.

        Use this method if FSSInfo is mentionned

        @param name: Name of the field
        @param instance: Content using this storage
        @param rdf_script: Script used to generate rdf args
        """

        default_rdf = self.getRDF(name, instance)
        rdf_args = None
        if rdf_script:
            func = getattr(instance, rdf_script, None)
            if func is not None:
                rdf_args = func(name=name, instance=instance, properties=self.getProperties(), default_rdf=default_rdf)

        if rdf_args is None:
            rdf_args = default_rdf
        writer = RDFWriter(**rdf_args)
        return writer.getRDF()

InitializeClass(FSSInfo)

class FSSFileInfo(FSSInfo):
    """FileSystemStorageInfo File class. Used for file data"""

    security = ClassSecurityInfo()

    def __init__(self, uid, title, size, mimetype):
        self.update(uid, title, size, mimetype)

    security.declarePrivate('update')
    def update(self, uid, title, size, mimetype):
        FSSInfo.update(self, uid)
        self.title = title
        self.size = size
        self.mimetype = mimetype

    security.declarePrivate('getTitle')
    def getTitle(self):
        return self.title

    security.declarePrivate('setTitle')
    def setTitle(self, title):
        self.title = title

    security.declarePrivate('getSize')
    def getSize(self):
        return self.size

    security.declarePrivate('setSize')
    def setSize(self, size):
        self.size = size

    security.declarePrivate('getMimetype')
    def getMimetype(self):
        return self.mimetype

    security.declarePrivate('setMimetype')
    def setMimetype(self, mimetype):
        self.mimetype = mimetype

    security.declarePrivate('getValue')
    def getValue(self, name, instance, path):
        return VirtualFile(name, instance, path, self.title, self.mimetype, self.size)

    security.declarePrivate('getProperties')
    def getProperties(self):
        """Returns info attributes in a dictionnary"""

        props = FSSInfo.getProperties(self)
        props['mimetype'] = self.mimetype
        props['title'] = self.title
        props['size'] = self.size
        return props

    security.declarePrivate('getRDFFieldProperties')
    def getRDFFieldProperties(self, name, instance):
        """Returns RDF field properties list.

        Each property is defined in a dictionnary {'id': ...,  'value': ...}

        @param name: name of the field
        @param instance: Content using this storage"""

        props = FSSInfo.getRDFFieldProperties(self, name, instance) + (
            {'id': 'fss:filename', 'value': self.title},
            {'id': 'fss:size', 'value': self.size},
            )
        return props

InitializeClass(FSSFileInfo)

class FSSImageInfo(FSSFileInfo):
    """FileSystemStorageInfo Image class. Used for image data"""

    security = ClassSecurityInfo()

    def __init__(self, uid, title, size, mimetype, width, height):
        self.update(uid, title, size, mimetype, width, height)

    security.declarePrivate('update')
    def update(self, uid, title, size, mimetype, width, height):
        FSSFileInfo.update(self, uid, title, size, mimetype)
        self.width = width
        self.height = height

    security.declarePrivate('getWidth')
    def getWidth(self):
        return self.width

    security.declarePrivate('setWidth')
    def setWidth(self, width):
        self.width = width

    security.declarePrivate('getHeight')
    def getHeight(self):
        return self.height

    security.declarePrivate('setHeight')
    def setHeight(self, height):
        self.height = height

    security.declarePrivate('getValue')
    def getValue(self, name, instance, path):
        return VirtualImage(name, instance, path, self.title, self.mimetype, self.size, self.width, self.height)

    security.declarePrivate('getProperties')
    def getProperties(self):
        """Returns info attributes in a dictionnary"""

        props = FSSFileInfo.getProperties(self)
        props['width'] = self.width
        props['height'] = self.height
        return props

    security.declarePrivate('getRDFFieldProperties')
    def getRDFFieldProperties(self, name, instance):
        """Returns RDF field properties list.

        Each property is defined in a dictionnary {'id': ...,  'value': ...}

        @param name: name of the field
        @param instance: Content using this storage"""

        props = FSSFileInfo.getRDFFieldProperties(self, name, instance) + (
            {'id': 'fss:width', 'value': self.width},
            {'id': 'fss:height', 'value': self.height},
            )
        return props

InitializeClass(FSSImageInfo)

# Keep it for compatibility
class FileSystemStorageInfo(FSSFileInfo):
    pass

InitializeClass(FileSystemStorageInfo)


# ####
# Storage
# ####

class FileSystemStorage(StorageLayer):

    __implements__ = StorageLayer.__implements__

    security = ClassSecurityInfo()

    security.declarePrivate('getFSSInfoVarname')
    def getFSSInfoVarname(self, name):
        """ """

        return '%s_filesystemstorage_info' % name

    security.declarePrivate('getFSSInfo')
    def getFSSInfo(self, name, instance, **kwargs):
        """Get fss info"""

        info_varname = self.getFSSInfoVarname(name)
        return getattr(aq_base(instance), info_varname, None)


    security.declarePrivate('delFSSInfo')
    def delFSSInfo(self, name, instance, **kwargs):
        """Delete fss info attribute"""

        info_varname = self.getFSSInfoVarname(name)
        delattr(aq_base(instance), info_varname)

    security.declarePrivate('setFSSInfo')
    def setFSSInfo(self, name, instance, value, **kwargs):
        """Set new value in fss info"""

        info_varname = self.getFSSInfoVarname(name)
        field = self.getField(name, instance, **kwargs)

        # Check types
        uid = instance.UID()
        if isinstance(value, File) or isinstance(value, Image):
            size = value.get_size()
            mimetype = kwargs.get('mimetype', getattr(value, 'content_type', 'application/octet-stream'))
            title = kwargs.get('filename', getattr(value, 'filename', getattr(value, 'title', name)))

            if isinstance(value, Image):
                width = value.width
                height = value.height
                if type(title) not in (StringType, UnicodeType):
                    # Make sure title is a string (Fix for image thumbs)
                    title = name

                # Like Image field
                info = FSSImageInfo(uid, title, size, mimetype, width, height)
            else:
                # Like File field
                info = FSSFileInfo(uid, title, size, mimetype)
        else:
            # Other
            info = FSSInfo(uid)

        # Make sure, we have deleted old info
        if hasattr(aq_base(instance), info_varname):
            delattr(instance, info_varname)

        # Store in attributes
        setattr(instance, info_varname, info)

        return info

    security.declarePrivate('getField')
    def getField(self, name, instance, **kwargs):
        """Get field"""

        return kwargs.get('field', instance.getField(name))

    def getInheritedNames(self, instance, field):
        """Returns all names derivating from a field

        Include field name it self. Then for example Image field size names
        """

        name = field.getName()

        # List of names created from one Field
        # Include field name
        # ImageField has size names (image_mini, image_thumb)
        names = [name]

        # This is a workaround for scales in ImageField
        if isinstance(field, ImageField):
            names.extend(['%s_%s' % (name, x) for x in field.getAvailableSizes(instance).keys()])

        return names

    def getStorageStrategy(self, name, instance):
        """Get strategy that defined how field values are stored"""

        fss_tool = getToolByName(instance, 'portal_fss')
        return fss_tool.getStorageStrategy()

    def getStorageStrategyProperties(self, name, instance, info):
        """Returns a dictionnary containing all properties used by
        strategies to store field values"""

        kwargs = {}
        kwargs['name'] = name
        utool = getToolByName(instance, 'portal_url')
        kwargs['path'] = '/'.join(utool.getRelativeContentPath(instance))
        kwargs.update(info.getProperties())
        return kwargs

    security.declarePrivate('get')
    def get(self, name, instance, **kwargs):
        """Get value of a field"""

        info = self.getFSSInfo(name, instance)

        if info is None:
            return ''

        strategy = self.getStorageStrategy(name, instance)
        props = self.getStorageStrategyProperties(name, instance, info)

        # Restore backup if exists
        strategy.restoreValueFile(**props)
        path = strategy.getValueFilePath(**props)
        return info.getValue(name, instance, path)

    security.declarePrivate('set')
    def set(self, name, instance, value, **kwargs):
        """Set value of a field"""

        # Ignore initialize process
        initializing = kwargs.get('_initializing_', False)
        if initializing:
            return

        # Remove acquisition wrappers
        value = aq_base(value)

        # Create File System Storage Info
        info = self.setFSSInfo(name, instance, value, **kwargs)

        # Wrap value
        if IObjectField.isImplementedBy(value):
            value = value.getRaw(self.instance)
        if IBaseUnit.isImplementedBy(value):
            value = value.getRaw()
        elif isinstance(value, File):
            value = value.data
        else:
            value = str(value)

        # Copy file on filesystem
        strategy = self.getStorageStrategy(name, instance)
        props = self.getStorageStrategyProperties(name, instance, info)
        strategy.setValueFile(value, **props)

        # Create RDF file
        fss_tool = getToolByName(instance, 'portal_fss')
        is_rdf_enabled = fss_tool.isRDFEnabled()
        rdf_script = fss_tool.getRDFScript()

        if is_rdf_enabled:
            # Replace rdf file
            rdf_value = info.getRDFValue(name, instance, rdf_script)
            strategy.setRDFFile(rdf_value, **props)

    security.declarePrivate('unset')
    def unset(self, name, instance, **kwargs):
        """Delete field value"""

        info = self.getFSSInfo(name, instance)

        if info is None:
            return

        # This method can be called when an object is cut/paste
        strategy = self.getStorageStrategy(name, instance)
        props = self.getStorageStrategyProperties(name, instance, info)
        is_moved = kwargs.get('is_moved', False)
        strategy.unsetValueFile(is_moved=is_moved, **props)
        strategy.unsetRDFFile(is_moved=is_moved, **props)

        # Delete field so delete fss attribute
        if not is_moved:
            # Store fss info in a volatile because it could be just a move
            # Check it in cleanupInstance method
            info = self.getFSSInfo(name, instance, **kwargs)
            fss_props = getattr(instance, '_v_fss_props', {})
            fss_props[name] = info
            setattr(instance, '_v_fss_props', fss_props)

            # Delete FSS info
            self.delFSSInfo(name, instance, **kwargs)

    security.declarePrivate('initializeField')
    def initializeField(self, instance, field, **kwargs):
        """Initialize field of object"""

        # Remove _v_fss_move attribute
        if hasattr(instance, '_v_fss_move'):
            delattr(instance, '_v_fss_move')

        name = field.getName()
        info = self.getFSSInfo(name, instance)

        if info is None:
            return

        names = self.getInheritedNames(instance, field)
        uid = instance.UID()
        src_uid = info.getUID()
        fss_tool = getToolByName(instance, 'portal_fss')
        is_rdf_enabled = fss_tool.isRDFEnabled()
        rdf_script = fss_tool.getRDFScript()
        strategy = self.getStorageStrategy(name, instance)

        if uid == src_uid:
            # Cut/Paste
            for name in names:
                info = self.getFSSInfo(name, instance)
                props = self.getStorageStrategyProperties(name, instance, info)
                strategy.restoreValueFile(**props)

                if is_rdf_enabled:
                    # Replace rdf file
                    rdf_value = info.getRDFValue(name, instance, rdf_script)
                    props = self.getStorageStrategyProperties(name, instance, info)
                    strategy.setRDFFile(rdf_value, **props)
        else:
            # Copy/Paste
            # Get source object
            atool= getToolByName(instance, 'archetype_tool')
            utool = getToolByName(instance, 'portal_url')
            src_obj = atool.getObject(src_uid)

            if src_obj is not None:
                src_path = '/'.join(utool.getRelativeContentPath(src_obj))

                for name in names:
                    info = self.getFSSInfo(name, instance)
                    info.setUID(uid)
                    props = self.getStorageStrategyProperties(name, instance, info)
                    strategy.copyValueFile(src_uid=src_uid, src_path=src_path, **props)

                    if is_rdf_enabled:
                        # Replace rdf file
                        rdf_value = info.getRDFValue(name, instance, rdf_script)
                        strategy.setRDFFile(rdf_value, **props)
            else:
                # Source object does not exist. Maybe object UID has been
                # changed using _setUID method
                for name in names:
                    info = self.getFSSInfo(name, instance)
                    info.setUID(uid)
                    props = self.getStorageStrategyProperties(name, instance, info)
                    strategy.moveValueFile(src_uid=src_uid, **props)

                    if is_rdf_enabled:
                        # Replace rdf file
                        rdf_value = info.getRDFValue(name, instance, rdf_script)
                        props = self.getStorageStrategyProperties(name, instance, info)
                        strategy.setRDFFile(rdf_value, **props)

    security.declarePrivate('cleanupField')
    def cleanupField(self, instance, field, **kwargs):
        """Delete object field"""

        # Is this object deleted or just cut/paste
        is_moved = getattr(instance, '_v_cp_refs', False)

        # Create special _v_fss_move attribute to avoid event bug in AT 1.4
        if is_moved:
            setattr(instance, '_v_fss_move', True)

        is_moved = getattr(instance, '_v_fss_move', False)

        # Remove field values
        name = field.getName()
        names = self.getInheritedNames(instance, field)

        for name in names:
            self.unset(name, instance, is_moved=is_moved, **kwargs)

    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        """Initialize new object"""

        # Not implemented
        pass

    security.declarePrivate('cleanupInstance')
    def cleanupInstance(self, instance, item=None, container=None):
        """Delete object"""

        if item is None:
            return

        # chekc if item is moved or really deleted
        is_moved = getattr(item, '_v_cp_refs', False)

        # If item is moved, apply, fss_move variable to instance
        if not is_moved:
            return

        fss_props = getattr(instance, '_v_fss_props', None)

        if fss_props is None:
            return

        for name, info in fss_props.items():
            fss_info_name = self.getFSSInfoVarname(name)
            setattr(instance, fss_info_name, info)

InitializeClass(FileSystemStorage)
