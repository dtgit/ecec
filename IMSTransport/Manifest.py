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

from Acquisition import aq_inner, aq_parent
from zope.interface import implements
from zope.event import notify
from interfaces import IIMSManifestWriter, IIMSManifestReader
from ManifestEvents import SetNameSpaces, ObjectWriteMetadata, ObjectReadMetadata, \
                           ObjectWriteOrganizations, ObjectReadOrganizations, \
                           ObjectCreateObject, ObjectTransformPackage
from IMS_exceptions import ManifestError
from zipfile import ZipFile, ZIP_DEFLATED
from cStringIO import StringIO
from xml.dom import minidom
from libxml2 import readFile, parseDoc
from libxslt import parseStylesheetDoc
from string import join
import md5
import os


IMS_schema = 'IMS CONTENT'
IMS_version = '1.2'


class IMSManifestWriter(object):
    """ Write an IMS content package manifest file. """

    implements(IIMSManifestWriter)

    namespaces = [('xmlns', 'http://www.imsglobal.org/xsd/imscp_v1p1'),
                  ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance'),]
    schema_locations = ['http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p2.xsd',]
    schema_files = [('Products.IMSTransport.IMS', 'imscp_v1p2.xsd')]


    def __init__(self, context):
        self.context = context
        self.document = None
        self.destination = None
        self.manifest_node = None


    def setWriterType(self, wtype):
        """ The writer type field acts as a selector for write manifest events.
            The Manifest writer will send this type when it fires an event.
            Event handlers written for the event should first check this value
            before executing any functionality. That way multiple event handlers
            can be subscribed, but only one event handler will execute the
            specified functionality. """
        self.wtype = wtype


    def setDestination(self, destination):
        """ Set the output object for the writer. """
        self.destination = destination

        
    def writeManifest(self):
        """ Write the manifest. """

        # Create an empyt XML document
        self.document = minidom.Document()

        # Create the Manifest node
        manifestId = self._createPathId(self.context.virtual_url_path(), 'MAN')
        manifestVer = self.context.ModificationDate()
        self.manifest_node = self._createNode(self.document,
                                              '',
                                              'manifest',
                                              attrs=[('identifier', manifestId),
                                                     ('xmlns:version', manifestVer)])
        self.addNamespace()
        notify(SetNameSpaces(self.context, self))

        # Create the top level Metadata node
        metadata_node = self._createNode(self.manifest_node, '', 'metadata')
        self._createNode(metadata_node, '', 'schema', IMS_schema)
        self._createNode(metadata_node, '', 'schemaversion', IMS_version)

        # Create the Organizations node
        defaultId = self._createPathId(self.context.virtual_url_path(), 'ORG')
        organizations_node = self._createNode(self.manifest_node,
                                              '',
                                              'organizations',
                                              attrs=[('default', defaultId)])

        # Send a write organizations event, so that anyone can do what they want here
        notify(ObjectWriteOrganizations(self.context, organizations_node, self))
        
        resources_node = self._createNode(self.manifest_node, '', 'resources')

        allObjects = self._getAllObjects()
        
        for obj in allObjects:
            # Handle the case where an object might be folderish, but
            # also has a text attribute.
            if not obj.isPrincipiaFolderish or hasattr(obj.aq_explicit,'getText'):
                path = self._getObjectPath(obj)
                self._writeResource(obj, resources_node, path)
                self._writeObjectData(obj, path)

        self._writeObjectData(self.getManifest(), 'imsmanifest.xml')

        os.chdir(os.environ['INSTANCE_HOME'])

        for x in self.schema_files:
            path = x[0].replace('.', os.sep)
            fn = os.path.join(path, x[1])
            f = open(fn, 'rb')
            schema = f.read()
            f.close()
            self._writeObjectData(schema, x[1])

        if self.destination:
            return self.destination.getOutput()
        else:
            return None, None

        
    def _writeObjectData(self, obj, path):
        """ Write file data to the destination object. """
        if type(obj) == type(''):
            data = obj        
        else:
            format = ''
            if hasattr(obj.aq_explicit, 'Format'):
                format = obj.Format()
            if 'Link' == obj.Type():
                doc = minidom.Document()
                anchor_node = self._createNode(doc, '', 'a', obj.Title())
                anchor_node.setAttribute('href', obj.getRemoteUrl())
                data = doc.toxml(encoding='utf-8')
            elif obj.Type() in ['File', 'Image']:
                if hasattr(obj.aq_explicit, 'data'):
                    data = obj.data
            elif 'text/html' == format:
                if hasattr(obj.aq_explicit, 'getText'):
                    data = obj.getText()
            elif format in ['text/plain', 'text/x-rst', 'text/structured']:
                if hasattr(obj.aq_explicit, 'getRawText'):
                    data = obj.getRawText()
            else:
                data = ''
        if self.destination:
            self.destination.writeFile(path, data)

    def _getAllObjects(self):
        """ Get all sub objects. """
        return [obj.getObject() for obj in self.context.portal_catalog.searchResults(path={'query':('/'.join(self.context.getPhysicalPath())+'/'),})]

    
    def _getObjectPath(self, obj):
        """ Get the path of an object. """

        path = obj.virtual_url_path().replace(self.context.aq_inner.aq_parent.virtual_url_path(), '')[1:]

        # If object has type text/html, and is also folderish, change the path
        # so that both a folder and an html file can be created.
        if hasattr(obj.aq_explicit, 'Format'):
            if 'text/html' == obj.Format() and obj.isPrincipiaFolderish:
                path += '.html'

        return path
        
    def _writeResource(self, obj, node, path):
        """ Write out a resource object """

        resourceId = self._createPathId(obj.virtual_url_path(), 'RES')
        resource_node = self._createNode(node,
                                         '',
                                         'resource',
                                         attrs=[('type', 'webcontent'),
                                                ('href', obj.renderBase()),
                                                ('identifier', resourceId)])
        
        metadata_node = self._createNode(resource_node, '', 'metadata')
        
        # Send a write metadata event, in case anyone wants to include custom metadata
        notify(ObjectWriteMetadata(aq_inner(obj), metadata_node, self))
        
        file_node = self._createNode(resource_node, '', 'file', attrs=[('href', path)])

        
    def _createPathId(self, path, pre='RES'):
        """ Create a unique id given a path """
        return pre + str(md5.md5(path).hexdigest())


    def getManifest(self):
        """ Get the manifest expressed in XML. """
        return self.document.toprettyxml(encoding='utf-8')


    def _createNode(self, parent, nspace, ename, value=None, attrs=None):
        """ Create a node in the document. """
        newnode = self.document.createElementNS(nspace, ename)
        parent.appendChild(newnode)
        if value and value != '':
            if not isinstance(value, unicode):
                newnode.appendChild(self.document.createTextNode(value.decode('utf-8')))
            else:
                newnode.appendChild(self.document.createTextNode(value))                
        if attrs:
            for x in attrs:
                newnode.setAttribute(x[0], x[1])
        return newnode


    def addNamespace(self, namespace=None, location=None, file=None):
        """ Add a namespace to the manifest. """
        if namespace:
            self.namespaces.append(namespace)
        if location and location not in self.schema_locations:
            self.schema_locations.append(location)
        if file and file not in self.schema_files:
            self.schema_files.append(file)
        for ns in self.namespaces:
            self.manifest_node.setAttribute(ns[0], ns[1])
        self.manifest_node.setAttribute('xsi:schemaLocation', join(self.schema_locations, ' '))


class FileWriter:
    """ Write files out to the file system """
    
    def __init__(self, package_name):
        self.fullpath = os.tempnam('var', 'OBJ')
        self.fullpath = os.path.join(self.fullpath, package_name)
        self._mkdirs(self.fullpath.split(os.sep))


    def _mkdirs(self, path):
        """ Make directory structure. """
        curdir = os.getcwd()
        if not len(path):
            return
        elif not os.path.exists(path[0]):
            os.mkdir(path[0])
        os.chdir(path[0])
        self._mkdirs(path[1:])
        os.chdir(curdir)

    
    def writeObject(self, obj, path):
        ''' Writes content object to the file system '''
        fullpath = self.fullpath
        for x in path.split('/'):
            fullpath = os.path.join(fullpath, x)
        self._mkdirs(fullpath.split(os.sep)[:-1])

        if hasattr(obj.aq_explicit, 'getText'):
            file = open(fullpath + '.html', 'w')
            file.write(obj.getText())
            file.close
            
        elif hasattr(obj.aq_explicit, 'data'):
            file = open(fullpath,'w')
            file.write(obj.data)
            file.close()

        
    def writeManifest(self, manifest):
        fullpath = os.path.join(self.fullpath, 'imsmanifest.xml')
        f = open(fullpath, 'wb')
        f.write(manifest)
        f.close()


class ZipfileWriter:
    """ Write a zip file which contains all the IMS Content packaging stuff. """

    def __init__(self, archive_name, package_name):
        self.fullpath = '%s/' %package_name
        self.archive_name = archive_name
        self.package_name = package_name
        self.archive = StringIO()
        self.zipfile = ZipFile(self.archive, 'w', ZIP_DEFLATED)


    def writeFile(self, path, data):
        """ Write a file to the zip archive. """
        fpath = '%s%s' %(self.fullpath, path)
        self.zipfile.writestr(fpath, data)


    def getOutput(self):
        """ Close the zip file and get the binary archive. """
        self.zipfile.close()
        self.archive.seek(0)
        return self.archive.read(), self.archive_name
        

class IMSManifestReader(object):
    """ Read an IMS content package manifest file. """

    implements(IIMSManifestReader)


    def __init__(self, context):
        """
        """
        self.context = context
        self.rtype = None
        self.source = None
        self.requiredMetadataSections = []


    def setReaderType(self, rtype):
        """ The reader type field acts as a selector for read manifest events.
            The manifest reader will send this type when it fires an event.
            Event handlers written for the event should first check this value
            before executing any functionality. That way multiple event handlers
            can be subscribed, but only one event handler will execute the
            specified functionality. """
        self.rtype = rtype


    def setSource(self, source):
        """ Set the source of the file data. """
        self.source = source


    def setRequiredMetadataSections(self, sections):
        """ Set which metadata sections should be required, so that
            an error can be thrown if a section is missing. """
        if type(sections) == type([]):
            for x in sections:
                self.requiredMetadataSections.append(x)
        else:
            self.requiredMetadataSections = [sections]


    def readManifest(self, package_type=None):
        """ Read the manifest """

        if self.source:
            manifest = self.source.readManifest()
            if not manifest:
                return False, \
                       'Manifest', \
                       'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
            
            xformdata = {} 
            if package_type:
                notify(ObjectTransformPackage(self, manifest, package_type, xformdata))

            if xformdata.has_key('manifest'):
                manifest = xformdata['manifest']
            if xformdata.has_key('filedata'):
                filedata = xformdata['filedata']
            else:
                filedata = {}
            
            self.document = minidom.parseString(manifest)

            try: 
                org = self.readOrganizations()
                resources = self.readResources(org)
            except ManifestError, e:
                return False, 'Manifest', e
            else:
                for res in resources:
                    for f in res[0]:
                        data = None
                        if self.source:
                            # If we already have data for the file, use it instead
                            if filedata.has_key(f):
                                data = filedata[f]
                            else:
                                data = self.source.readFile(f)
                        if data:
                            notify(ObjectCreateObject(self.context, self.rtype, str(f), data, res[1]))
            return True, ''
        else:
            return False, 'Internal error. No source object specified.'

                
    def readOrganizations(self):
        """ Read the organizations section of the manifest. """
        org = {}
        organizations = self.document.getElementsByTagName('organizations')
        if organizations:
            notify(ObjectReadOrganizations(self.context, organizations[0], self, org))
        else:
            raise ManifestError, 'Manifest file has no "organizations" section.'
        return org


    def readResources(self, org):
        """ Read all resources. """
        allResources = []
        resources = self.document.getElementsByTagName('resources')
        if resources:
            for res in resources[0].getElementsByTagName('resource'):
                metadata = {}
                # Check to see if navigations options should be set
                id = res.getAttribute('identifier')
                if id:
                    if org.has_key(id):
                        metadata['excludeFromNav'] = False
                        metadata['navPosition'] = org[id]
    
                    else:
                        metadata['excludeFromNav'] = True
                # Get metadata for objects
                files = []
                file_nodes = res.getElementsByTagName('file')
                for f in file_nodes:
                    fn = f.getAttribute('href')  
                    if fn: 
                        files.append(fn) 
                if not files:
                    raise ManifestError, 'Missing "file" tag in resource %s.' %id

                # Create the objects
                self.readMetadata(res, metadata, id)
                allResources.append((files, metadata))

        return allResources


    def readMetadata(self, node, metadata, resid):
        """ Get the metadata, and set it on an object """
        metadata_node = node.getElementsByTagName('metadata')
        if metadata_node:
            mdSections = []
            for md in metadata_node[0].childNodes:
                if md.nodeType == md.ELEMENT_NODE:
                    notify(ObjectReadMetadata(self.context, metadata, md, self, mdSections, resid))
            for x in self.requiredMetadataSections:
                if x not in mdSections:
                    raise ManifestError, \
                          'Missing required metadata section "%s" for resource "%s".' %(x, resid)
        else:
            raise ManifestError, 'Missing required "metadata" section in resource "%s".' %resid
        return metadata


    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None
                                
    
    def getVcardValues(self, node, resid):
        """
        Looks for the full name and email values in a VCARD
        value.

        Added some whitespace stripping, and case
        insensitive tag searching, so that we could parse the
        default IMS example package.
    
        """
        text = self.getTextValue(node)
        textlines = text.strip().split('\n')
                
        value = self._getVcardValue('BEGIN', [textlines[0]])
        if 'VCARD' != value.strip().upper():
            raise ManifestError, 'Missing VCARD BEGIN tag for resource "%s"' %resid

        value = self._getVcardValue('END', [textlines[-1]])
        if 'VCARD' != value.strip().upper():
            raise ManifestError, 'Missing VCARD END tag for resource "%s"' %resid
            
        name = self._getVcardValue('FN', textlines)
        email = self._getVcardValue('EMAIL;INTERNET', textlines)

        return name, email

        
    def _getVcardValue(self, field, text):
        """ Try to get a value for a VCARD field. """
        for textline in text:
            # If the line is not folded
            #if textline[0] != ' ':
                # Look for the Colon delimiter
            textline = textline.strip()
            if textline.find(':'):
                tag = textline.split(':')
                if field == tag[0].upper().strip():
                    return tag[1].strip()
        else:
            return ''
                

    def _importFile(self, file_node):
        ''' Get the file '''
        pass


    def performTransform(self, manifest, package_type):
        """ Transform the manifest if necessary. """
        if package_type:
            xform = os.path.join(INSTANCE_HOME, 'Products', 'IMSTransport', 'IMS', package_type[1])
            styledoc = readFile(xform, None, 0)
            style = parseStylesheetDoc(styledoc)
            doc = parseDoc(manifest)
            manifest = ''
            result = style.applyStylesheet(doc, None)
            if result and result.get_content():
                manifest = style.saveResultToString(result)
            style.freeStylesheet()
            doc.freeDoc()
            result.freeDoc()
        return manifest


class FileReader:
    """ Read files from the var directory. """

    def __init__(self, package_path):
        self.fullpath = package_path


    def readManifest(self):
        """ Get the manifest file if it exists. """
        manifest_path = os.path.join(self.fullpath, 'imsmanifest.xml')
        file = open(manifest_path, 'rb')
        manifest = file.read()
        file.close()
        return manifest

    def readFile(self, path):
        """ Get file data from the zip file. """
        fullpath = self.fullpath
        for x in path.split('/'):
            fullpath = os.path.join(fullpath, x)
        file = open(fullpath, 'rb')
        data = file.read()
        file.close()
        return data


class ZipfileReader:
    """ Reads files from an imported zip file. """

    def __init__(self, files):
        self.files = ZipFile(files)
        self.fullpath = ''


    def readManifest(self):
        """ Get the maifest file if it exists. """
        for x in self.files.namelist():
            index = x.find('imsmanifest.xml')
            if index != -1:
                self.fullpath = x[:index]
                return self.files.read(x)
        return None
    

    def readFile(self, path):
        """ Get file data from the zip file. """
        fn = '%s%s' %(self.fullpath, str(path))
        if fn not in self.files.namelist():
            fn = fn.replace('/', '\\')
            if fn not in self.files.namelist():
                return None
        return self.files.read(fn)

    def listFiles(self):
        """ List files in the package. """
        return self.files.namelist()
