#################################################################################
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



from zope.event import notify
from Products.CMFCore.utils import UniqueObject, getToolByName
from ManifestEvents import ObjectWriteContributeNode, ObjectReadContributeNode, \
                           ObjectTransformPackage
from IMS_exceptions import ManifestError
import string
from mimetypes import guess_type
import re
from xml.dom import minidom


RE_BODY = re.compile('<body[^>]*?>(.*)</body>', re.DOTALL )
LOM_version = 'LOMv1.0'
LOM_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'

def setNameSpaces(event):
    """ Set name spaces for manifest file. """
    event.writer.addNamespace(('xmlns:imsmd', LOM_namespace),
                              'http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd',
                              ('Products.IMSTransport.IMS', 'imsmd_v1p2p4.xsd'))

class WriteLOMMetadata:
    """ Handle a write LOM metadata event, and write the metadata for an object. """

    def __call__(self, event):
        """ Catch the write metadata event. """
        self.writeMetadata(event.object, event.node, event.writer)


    def writeMetadata(self, object, node, writer):
        """ Write out the metadata. """

        rights_holder = object.portal_properties.site_properties.getProperty('rights_holder')
        rights_holder_email = object.portal_properties.site_properties.getProperty('rights_holduer_email')
        language = self.getLanguage(object)
        
        # LOM Node
        lom_node = writer._createNode(node,
                                      LOM_namespace,
                                      'lom',
                                      attrs=[('xmlns', LOM_namespace)])

        # General Node
        general_node = writer._createNode(lom_node, LOM_namespace, 'general')
        writer._createNode(general_node, LOM_namespace, 'identifier', object.getId())
        title_node = writer._createNode(general_node, LOM_namespace, 'title')
        writer._createNode(title_node,
                           LOM_namespace,
                           'langstring',
                           object.Title(),
                           [('xml:lang', language)])
        if language:
            writer._createNode(general_node, LOM_namespace, 'language', language)
        description = object.Description()
        if description:
            desc_node = writer._createNode(general_node, LOM_namespace, 'description')
            writer._createNode(desc_node,
                               LOM_namespace,
                               'langstring',
                               description,
                               [('xml:lang', language)])
        keywords = object.Subject()
        if keywords:
            keyword_node = writer._createNode(general_node, LOM_namespace, 'keyword')
            for kw in keywords:
                writer._createNode(keyword_node,
                                   LOM_namespace,
                                   'langstring',
                                   kw,
                                   [('xml:lang', language)])

        # Lifecycle Node
        lifecycle_node = writer._createNode(lom_node, LOM_namespace, 'lifecycle')
        notify(ObjectWriteContributeNode(object, lifecycle_node, writer, self))
                                     
        # Meta-Metadata Node
        metametadata_node = writer._createNode(lom_node, LOM_namespace, 'metametadata')
        catalog_node = writer._createNode(metametadata_node, LOM_namespace, 'catalogentry')
        writer._createNode(catalog_node,
                           LOM_namespace,
                           'catalog',
                           '%s,%s' %(object.portal_url(),
                                     object.portal_url.getPortalObject().getProperty('email_from_address')))
        entry_node = writer._createNode(catalog_node, LOM_namespace, 'entry')
        writer._createNode(entry_node,
                           LOM_namespace,
                           'langstring',
                           object.id,
                           [('xml:lang', 'x-none')])
        contributors = object.Contributors()
        if contributors:
            self.createContributeElement(writer,
                                         LOM_namespace,
                                         metametadata_node,
                                         LOM_version,
                                         'creator',
                                         contributors,
                                         object.ModificationDate())        
        writer._createNode(metametadata_node, LOM_namespace, 'metadatascheme', LOM_version)
        if language:
            writer._createNode(metametadata_node, LOM_namespace, 'language', language)

        # Technical Node
        technical_node = writer._createNode(lom_node, LOM_namespace, 'technical')
        writer._createNode(technical_node, LOM_namespace, 'format', object.Format())
        writer._createNode(technical_node, LOM_namespace, 'size', self.getObjSize(object))
        writer._createNode(technical_node, LOM_namespace, 'location', object.renderBase())

        # Rights Node
        rights_node = writer._createNode(lom_node, LOM_namespace, 'rights')
        copyright_other_node = writer._createNode(rights_node,
                                                  LOM_namespace,
                                                  'copyrightandotherrestrictions')
        source_node = writer._createNode(copyright_other_node, LOM_namespace, 'source')           
        writer._createNode(source_node,
                           LOM_namespace,
                           'langstring',
                           LOM_version,
                           [('xml:lang', 'x-none')])
        value_node = writer._createNode(copyright_other_node, LOM_namespace, 'value')
        writer._createNode(value_node,
                           LOM_namespace,
                           'langstring',
                           'yes',
                           [('xml:lang', 'x-none')])
        description_node = writer._createNode(rights_node, LOM_namespace, 'description')
        writer._createNode(description_node,
                           LOM_namespace,
                           'langstring',
                           self.getCopyrightString(object.Rights(), rights_holder, rights_holder_email),
                           [('xml:lang', 'x-none')])

    def createContributeElement(self, writer, nspace, lc_node, source, value, entities, date, email=None):
        """
           Create a LOM contribute node in the form

               <imsmd:contribute>
                   <imsmd:role>
                       <imsmd:source>
                           <imsmd:langstring xml:lang="x-none">
                               LOMv1.0
                           </imsmd:langstring>
                       </imsmd:source>
                       <imsmd:value>
                           <imsmd:langstring xml:lang="x-none">
                               author
                           </imsmd:langstring>
                       </imsmd:value>    
                   </imsmd:role>
                   <imsmd:centity>
                       <imsmd:vcard>
                           BEGIN:
                               NAME: Me
                           END:
                       </imsmd:vcard>
                   </imsmd:centity>
                   <imsmd:date>
                       <imsmd:datetime>
                           2006-01-01
                       </imsmd:datetime>
                   </imsmd:date>
               </imsmd:contribute>
        """
        contribute_node = writer._createNode(lc_node, nspace, 'contribute')
        role_node = writer._createNode(contribute_node, nspace, 'role')
        source_node = writer._createNode(role_node, nspace, 'source')
        writer._createNode(source_node,
                           nspace,
                           'langstring',
                           source,
                           [('xml:lang', 'x-none')])
        value_node = writer._createNode(role_node, nspace, 'value')
        writer._createNode(value_node,
                           nspace,
                           'langstring',
                           value,
                           [('xml:lang', 'x-none')])
        if entities:
            if type(entities) not in [type([]), type(())]:
                entities = [entities]
            for e in entities:
                centity_node = writer._createNode(contribute_node, nspace, 'centity')
                writer._createNode(centity_node,
                                   nspace,
                                   'vcard',
                                   self.createVCard(e, email))
        if date:
            date_node = writer._createNode(contribute_node, nspace, 'date')
            writer._createNode(date_node, nspace, 'datetime', date)

    def createVCard(self, name, email=None):
         """
         Writes out a VCard entry for a contribute element

         Note: Should replace this with the python vcard library.

         """
         vCard = 'BEGIN:VCARD\n'
         vCard += 'FN:'+name+'\n'
         if email:
             vCard += 'EMAIL;INTERNET:'+email+'\n'
         vCard += 'END:VCARD'
         return vCard

    def getObjSize(self, object):
        """ Retrieves the correct size of the object"""
        return '%d' %object.get_size()

    def getLanguage(self, object):
        """ Get Language setting """
        lang = object.Language()
        if not lang:
            lang = object.portal_properties.site_properties.getProperty('default_language')
        return lang

    def getCopyrightString(self, copyright, rights_holder, rights_holder_email):
        cp = ''
        if copyright:
            cp += copyright
        if rights_holder:
            if cp:
                cp += ', '
            cp += rights_holder
        if rights_holder_email:
            if cp:
                cp += ', '
            cp += rights_holder_email
        return cp
            
         
WriteLOMMetadataHandler = WriteLOMMetadata()


class WriteOrganizations:
    """ Handle a write organizations event, and write the organization information."""
    
    def __call__(self, event):
        """ Catch the write metadata event. """
        self._writeOrganizations(event.object, event.node, event.writer)
        
    def _writeOrganizations(self, object, node, writer):
        """ Write items that should appear in the navigation within the organizations section """
        pass


        
WriteOrganizationsHandler = WriteOrganizations()


class ReadOrganizations:
    """ Handle a read organizations event, and read the organization information."""
    
    def __call__(self, event):
        """ Catch the read metadata event. """
        self._readOrganizations(event.object, event.org, event.node, event.reader)

    def _readOrganizations(self, object, org, node, reader):
        """ Handle read organizations event. """
        default = node.getAttribute('default')
        organization_nodes = node.getElementsByTagName('organization')
        if organization_nodes:
            if default:
                for org_node in organization_nodes:
                    if org_node.getAttribute('identifier') == default:
                        organization_node = org_node
                        break
            else:
                organization_node = organization_nodes[0]
            
            item_nodes = organization_nodes[0].getElementsByTagName('item')
            itemnum = 1
            for item in item_nodes:
                if 'true' == item.getAttribute('isvisible'):
                    idref = item.getAttribute('identifierref')
                    org[idref] = itemnum
                    itemnum += 1


ReadOrganizationsHandler = ReadOrganizations()


class ReadLOMMetadata:
    """ Handle a read LOM metadata event, and read the metadata for an object. """

    def __call__(self, event):
        self.readMetadata(event.object,
                          event.metadata,
                          event.node,
                          event.reader,
                          event.mdSections,
                          event.resid)

    def readMetadata(self, object, metadata, node, reader, mdSections, resid):
        """ Create an object and set the metadata on it. """

        mdSections.append(LOM_version)

        if node.nodeName in ['lom', 'imsmd:lom']:

            gen_nodes = node.getElementsByTagNameNS(LOM_namespace, 'general')
            if gen_nodes:
                self.readGeneral(object, metadata, gen_nodes[0], reader, resid)
            else:
                raise ManifestError, 'No "general" tag found in metadata section for resource %s.' %resid

            lifecycle_nodes = node.getElementsByTagNameNS(LOM_namespace, 'lifecycle')
            if lifecycle_nodes:
                self.readLifecycle(object, metadata, lifecycle_nodes[0], reader, resid)

            metametadata_nodes = node.getElementsByTagNameNS(LOM_namespace, 'metametadata')
            if metametadata_nodes:
                self.readMetametadata(object, metadata, metametadata_nodes[0], reader)

            technical_nodes = node.getElementsByTagNameNS(LOM_namespace, 'technical')
            if technical_nodes:
                self.readTechnical(object, metadata, technical_nodes[0], reader, resid)

            rights_nodes = node.getElementsByTagNameNS(LOM_namespace, 'rights')
            if rights_nodes:
                self.readRights(object, metadata, rights_nodes[0], reader)


    def readGeneral(self, object, metadata, node, reader, resid):
        """ Read general node """

        title_nodes = node.getElementsByTagNameNS(LOM_namespace, 'title')        
        if title_nodes:
            langstring_nodes = title_nodes[0].getElementsByTagNameNS(LOM_namespace,
                                                                     'langstring')
            if langstring_nodes:
                title = reader.getTextValue(langstring_nodes[0])
                if title:
                    metadata['title'] = title
        
        if not metadata.has_key('title'):
            raise ManifestError, 'Required tag "title" missing in lom/general metadata section for resource %s.' %resid

        language_nodes = node.getElementsByTagNameNS(LOM_namespace, 'language')
        if language_nodes:
            lang = reader.getTextValue(language_nodes[0])
            if lang:
                metadata['language'] = lang

        desc_nodes = node.getElementsByTagNameNS(LOM_namespace, 'description')
        if desc_nodes:
            langstring_nodes = desc_nodes[0].getElementsByTagNameNS(LOM_namespace,
                                                                    'langstring')
            if langstring_nodes:
                description = reader.getTextValue(langstring_nodes[0])
                if description:
                    metadata['description'] = description

        kw_nodes = node.getElementsByTagNameNS(LOM_namespace, 'keyword')
        if kw_nodes:
            kw_lang_nodes = kw_nodes[0].getElementsByTagNameNS(LOM_namespace,'langstring')
            if kw_lang_nodes:
                kw_list = []
                for lang_node in kw_lang_nodes:
                    kw = reader.getTextValue(lang_node)
                    if kw:
                        kw_list.append(kw)
            if kw_list:
                metadata['subject'] = kw_list


    def readLifecycle(self, object, metadata, node, reader, resid):
        """ Read Lifecycle node """
        # Lifecycle Node
        contribute_nodes = node.getElementsByTagNameNS(LOM_namespace, 'contribute')
        
        # For each contribute node there is a role node, a centity node, and possibly a date node
        for contribute_node in contribute_nodes:
            source = ''
            value = ''
            vlist = []
            date = ''
            
            role_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'role')
            if role_nodes:
                source_nodes = role_nodes[0].getElementsByTagNameNS(LOM_namespace, 'source')
                if source_nodes:
                    langstring_nodes = source_nodes[0].getElementsByTagNameNS(LOM_namespace, 'langstring')
                    if langstring_nodes:
                        source = reader.getTextValue(langstring_nodes[0])
                value_nodes = role_nodes[0].getElementsByTagNameNS(LOM_namespace, 'value')
                if value_nodes:
                    langstring_nodes = value_nodes[0].getElementsByTagNameNS(LOM_namespace, 'langstring')
                    if langstring_nodes:
                        value = reader.getTextValue(langstring_nodes[0])

            centity_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'centity')
            for centity_node in centity_nodes:
                for cnode in centity_node.childNodes:
                    if cnode.nodeType == cnode.ELEMENT_NODE:
                        name, email = reader.getVcardValues(cnode, resid)
                        if value:
                            vlist.append((name, email))
                
            date_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'date')
            if date_nodes:
                datetime_nodes = date_nodes[0].getElementsByTagNameNS(LOM_namespace, 'datetime')
                if datetime_nodes:
                    datetime = reader.getTextValue(datetime_nodes[0])

            notify(ObjectReadContributeNode(object, metadata, source, value, vlist, date))
            

    def readMetametadata(self, object, metadata, node, reader):
        """ Read Meta-metadata node """
        pass

    def readTechnical(self, object, metadata, node, reader, resid):
        """ Read Technical node """
        format_nodes = node.getElementsByTagNameNS(LOM_namespace, 'format')
        if format_nodes:
            format = reader.getTextValue(format_nodes[0])
            if format:
                metadata['Format'] = format
        #if not metadata.has_key('Format'):
        #    raise ManifestError, \
        #          'Required tag "format" missing in lom/technical metadata section for resource %s.' %resid
        
    def readRights(self, object, metadata, node, reader):
        """ Read Rights node """
        
        description_nodes = node.getElementsByTagNameNS(LOM_namespace,'description')
        if description_nodes:
            langstring_nodes = description_nodes[0].getElementsByTagNameNS(LOM_namespace,'langstring')
            if langstring_nodes:
                description = reader.getTextValue(langstring_nodes[0])
                if description:
                    metadata['rights'] = description


        
ReadLOMMetadataHandler = ReadLOMMetadata()


def writeContributeNode(event):
    """ Write a LOM contribute node. """
    creators = event.object.Creators()
    if creators:
        event.mwriter.createContributeElement(event.writer,
                                              LOM_namespace,
                                              event.node,
                                              LOM_version,
                                              'author',
                                              creators,
                                              event.object.ModificationDate())
    contributors = event.object.Contributors()
    if contributors:
        event.mwriter.createContributeElement(event.writer,
                                              LOM_namespace,
                                              event.node,
                                              LOM_version,
                                              'unknown',
                                              contributors,
                                              event.object.ModificationDate())
    


def readContributeNode(event):
    """ Read a LOM contribute Node. """

    if LOM_version == event.source:

        # Creator
        if 'author' == event.value.lower() and event.vlist:
            event.metadata['creators'] = [x[0] for x in event.vlist]
            if event.date:
                event.metadata['creation_date'] = event.date

        # Contributors
        if 'unknown' == event.value.lower() and event.vlist:
            event.metadata['contributors'] = [x[0] for x in event.vlist]



class createObjects:
    """ Create new objects. """

    def __init__(self):
        pass

    def __call__(self, event):
        if 'IMSTransport' == event.rtype:
            self.createObject(event.object, event.resource, event.data, event.metadata)

    def createObject(self, object, filepath, data, metadata):
        """ Create an object with the given parameters. """
        # Get info
        objtype = self.getObjectType(filepath, metadata)
        parent = self.createFolders(filepath, objtype, object)
        newobj = self.getNewObject(filepath, objtype, object, parent)
        self.setObjectData(filepath, objtype, object, newobj, data, metadata)
                 

    def getObjectType(self, filepath, metadata):
        """ Get the type of the object. """

        objtype='File'
        if metadata.has_key('Type'):
            # Get type from resource metadata
            objtype = metadata['Type']
        elif metadata.has_key('ResType'):
            # Get type from resource tag
            objtype = metadata['ResType']
        else:
            # Get object type from mimetype
            if metadata.has_key('Format'):
                # Get the mimetype out of this field
                restype = metadata['Format']
            else:
                # Get the mimetype from the mimetype library
                restype = guess_type(filepath)[0]
            if restype:
                # Set object type based on mimetype
                if restype in ['text/html', 'text/htm' 'text/plain' 'text/x-rst', 'text/structured']:
                    objtype = 'Document'
                elif re.match('^image', restype):
                    objtype = 'Image'
                else:
                    objtype = 'File'

        return objtype
                
            
    def createFolders(self, filepath, objtype, object):
        """ Create folders for the object if they do not already exist. """
        parent = object

        if objtype != 'Folder':
            # Get the ZODB path, create folders if they do not exist
            for p in filepath.split('/')[:-1]:
                newparent = getattr(parent.aq_explicit, p, None)
                if newparent:
                    parent = newparent
                else:
                    parent = self.createFolder(parent, p)
                    parent.title = parent.id

        return parent


    def getNewObject(self, filepath, objtype, object, parent):
        """ Get the new object if it exists, otherwise create it. """
        id = filepath.split('/')[-1]
        newobj = None
        if parent == object and object.portal_type == objtype:
            newobj = object
        elif getattr(parent.aq_explicit, id, None):
            # The parent node has the object in it
            childobj = getattr(parent, id)
            # Check to see if the child node is the same type
            # as the new object, as we are going to be rewriting
            # all of its values.
            if childobj.portal_type == objtype:
                newobj = childobj
            else:
                # We need to delete this object, as it is not
                # the same type as the one we are trying to
                # upload.
                parent.manage_delObjects([id])

        # If we do not already have an object, create a new one
        if not newobj:
            parent.invokeFactory(objtype, id)
            newobj = getattr(parent, id)
            newobj = object.portal_factory.doCreate(newobj, id)

        return newobj


    def setObjectData(self, filepath, objtype, object, newobj, data, metadata):
        """ Set the file data on the object. """
        if objtype == 'Document':
            if metadata.has_key('Format'):
                fmt = metadata['Format']
            else:
                fmt = guess_type(filepath)[0]
            newobj.setText(data, mimetype=fmt, filename=filepath.split('/')[-1])           
        elif 'File' == objtype:
            newobj.setFile(data)
        elif 'Image' == objtype:
            newobj.setImage(data)
        elif 'Link' == objtype:
            newobj.setRemoteUrl(data)
        
        # Set the metadata on the object
        for key in metadata.keys():
            field = newobj.getField(key)
            if field:
                mutator = field.getMutator(newobj)
                if mutator:
                    if field.__name__ == 'excludeFromNav':
                        mutator('False')
                    else:
                        mutator(metadata[key])
                    
        # Reindex the object so that the new stuff appears
        object.portal_catalog.reindexObject(newobj, object.portal_catalog.indexes() )


    def createFolder(self, parent, id):
        """ Create a folder """

        parent.invokeFactory('Folder',id)
        obj = getattr(parent, id)
        obj.setExcludeFromNav(True)
        obj.setTitle(id)
        obj = parent.portal_factory.doCreate(obj, id)
        
        parent.portal_catalog.reindexObject(obj, parent.portal_catalog.indexes())

        return obj

    def stripHeader(self, data):
        """ Tidy up any html, if we can. """
        # get the body text
        result = RE_BODY.search(data)
        if result:
            data = result.group(1)
        return data

DefaultCreateObjects = createObjects()
