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
__version__ = "$Revision: 3026 $"[11:-2]

# eventHandlers.py


from Products.eduCommons.interfaces import ICourse, IDivision
from Products.IMSTransport.ManifestHandlers import LOM_namespace
from Products.IMSTransport.IMS_exceptions import ManifestError
from Products.CMFDefault.SyndicationTool import SyndicationTool
from Products.CMFDefault.SyndicationInfo import SyndicationInformation
from Products.ContentLicensing.utilities.interfaces import IContentLicensingUtility
from Products.ZipFileTransport.utilities.interfaces import IZipFileTransportUtility
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IContainerModifiedEvent

from zope.schema.interfaces import IVocabularyFactory
from zope.formlib.form import action
from Products.IMSTransport.browser.imstransportform import ImportForm
from utilities.interfaces import IECUtility
from zope.component import getUtility, queryUtility
import transaction
from xml.dom import minidom
import mimetypes
import re
from App.config import getConfiguration
import os


RE_BODY = re.compile('<body[^>]*?>(.*)</body>', re.DOTALL )

eduCommons_version = 'eduCommonsv1.2'
ec_namespace = 'http://cosl.usu.edu/xsd/eduCommonsv1.2'

def setNameSpaces(event):
    """ Set up namespaces in manifest file """
    event.writer.addNamespace(('xmlns:eduCommons', 'http://cosl.usu.edu/xsd/eduCommonsv1.2'), 
                              'http://cosl.usu.edu/xsd/eduCommonsv1.2 eduCommonsv1.2.xsd',
                              ('Products.eduCommons.IMS', 'eduCommonsv1.2.xsd'))
                              


def writeECMetadata(event):
    """ Handle write IMS metadata event, and add custom eduCommons metadata """

    event.writer.addNamespace(('xmlns:eduCommons', 'http://cosl.usu.edu/xsd/eduCommonsv1.2'), 
                              ('http://cosl.usu.edu/xsd/eduCommonsv1.2 eduCommonsv1.2.xsd'))
    eduCommons_node = event.writer._createNode(event.node,
                                               ec_namespace,
                                               'eduCommons',
                                               attrs=[('xmlns', ec_namespace)])

    objType = event.object.Type()
    if 'Page' == objType:
        objType = 'Document'
    if 'Link' == objType:
        objType = 'Link'
    event.writer._createNode(eduCommons_node, ec_namespace, 'objectType', objType)
    copyright = event.object.Rights()
    if copyright:
        event.writer._createNode(eduCommons_node, ec_namespace, 'copyright', copyright)

    cltool = getUtility(IContentLicensingUtility)
    linfo = cltool.getLicenseAndHolderFromObject(event.object)
    if linfo and linfo[1]:
        license = linfo[1]
        license_node = event.writer._createNode(eduCommons_node,
                                                ec_namespace,
                                                'license',
                                                attrs=[('category', license[0])])
        if license[1] and license[1] != 'None':
            event.writer._createNode(license_node, ec_namespace, 'licenseName', license[1])
        if license[2] and license[2] != 'None':
            event.writer._createNode(license_node, ec_namespace, 'licenseUrl', license[2])
        if license[3] and license[3] != 'None':
            event.writer._createNode(license_node, ec_namespace, 'licenseIconUrl', license[3])

    if IAnnotations(event.object).has_key('eduCommons.clearcopyright'):  
        event.writer._createNode(eduCommons_node, ec_namespace, 'clearedCopyright', 'true')
    else:
        event.writer._createNode(eduCommons_node, ec_namespace, 'clearedCopyright', 'false')

    #access = IAnnotations(event.object)['eduCommons.accessible']
    #if access:
    #    event.writer._createNode(eduCommons_node, ec_namespace, 'accessible', 'true')
    #else:
    #    event.writer._createNode(eduCommons_node, ec_namespace, 'accessible', 'false')

    if 'Course' == event.object.Type():
        courseId = event.object.getCourseId()
        if courseId:
            event.writer._createNode(eduCommons_node, ec_namespace, 'courseId', courseId)
        term = event.object.getTerm()
        if term:
            event.writer._createNode(eduCommons_node, ec_namespace, 'term', term)
        if True == event.object.getDisplayInstEmail():
            event.writer._createNode(eduCommons_node,
                                     ec_namespace,
                                     'displayInstEmail',
                                     'true')
        else:
            event.writer._createNode(eduCommons_node,
                                     ec_namespace,
                                     'displayInstEmail',
                                     'false')

        if True == event.object.getInstructorAsCreator():
            event.writer._createNode(eduCommons_node,
                                     ec_namespace,
                                     'instructorAsCreator',
                                     'true')
        else:
            event.writer._createNode(eduCommons_node,
                                     ec_namespace,
                                     'instructorAsCreator',
                                     'false')


def readECMetadata(event):
    """ Handle read IMS metadata event, and add custom eduCommons metadata """


    if event.node.nodeName in ['eduCommons', 'eduCommons:eduCommons']:
        
        event.mdSections.append(eduCommons_version)
         
        objectType_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'objectType')
        if objectType_nodes:
            ot = event.reader.getTextValue(objectType_nodes[0])
            if ot:
                if ot not in ['Course', 'FSSFile', 'Document', 'File', 'Image', 'Link']:
                    raise ManifestError, '"%s" is not a recognized object type.' %ot
                event.metadata['Type'] = '%s' %ot

        copyright_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'copyright')
        if copyright_nodes:
            cn = event.reader.getTextValue(copyright_nodes[0])
            if cn:
                event.metadata['rights'] = cn

        license_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'license')
        if license_nodes:
            license_node = license_nodes[0]
            license = [str(license_node.getAttribute('category'))]
            licenseName_nodes = license_node.getElementsByTagNameNS(ec_namespace, 'licenseName')
            if licenseName_nodes:
                license.append(str(event.reader.getTextValue(licenseName_nodes[0])))
            else:
                license.append('None')
            licenseUrl_nodes = license_node.getElementsByTagNameNS(ec_namespace, 'licenseUrl')
            if licenseUrl_nodes:
                license.append(str(event.reader.getTextValue(licenseUrl_nodes[0])))
            else:
                license.append('None')
            licenseIconUrl_nodes = license_node.getElementsByTagNameNS(ec_namespace, 'licenseIconUrl')
            if licenseIconUrl_nodes:
                license.append(str(event.reader.getTextValue(licenseIconUrl_nodes[0])))
            else:
                license.append('None')
            event.metadata['license'] = license

        clearedCopyright_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'clearedCopyright')
        if clearedCopyright_nodes:
            cc = event.reader.getTextValue(clearedCopyright_nodes[0])
            if 'true' == cc:
                event.metadata['clearedCopyright'] = True
            else:
                event.metadata['clearedCopyright'] = False

        accessibility_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'accessible')
        if accessibility_nodes:
            access = event.reader.getTextValue(accessibility_nodes[0])
            if 'true' == access:
                event.metadata['accessible'] = True
            else:
                event.metadata['accessible'] = False

        courseId_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'courseId')
        if courseId_nodes:
            cin = event.reader.getTextValue(courseId_nodes[0])
            if cin:
                event.metadata['courseId'] = cin
                
        term_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'term')
        if term_nodes:
            tm = event.reader.getTextValue(term_nodes[0])
            if tm:
                event.metadata['term'] = tm
                
        displayInsEmail_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'displayInstEmail')
        if displayInsEmail_nodes:
            die = event.reader.getTextValue(displayInsEmail_nodes[0])
            if 'true' == die:
                event.metadata['displayInstEmail'] = True
            else:
                event.metadata['displayInstEmail'] = False

        instrIsPrincipal_nodes = event.node.getElementsByTagNameNS(ec_namespace, 'instructorAsCreator')
        if instrIsPrincipal_nodes:
            iis = event.reader.getTextValue(instrIsPrincipal_nodes[0])
            if 'true' == iis:
                event.metadata['instructorAsCreator'] = True
            else:
                event.metadata['instructorAsCreator'] = False

        excludeFromNav_nodes = event.node.getElementsByTagNameNS(ec_namespace,'excludeFromNav')
        if excludeFromNav_nodes:
            efn = event.reader.getTextValue(excludeFromNav_nodes[0])
            if 'true' == efn:
                event.metadata['excludeFromNav'] = True
            else:
                event.metadata['excludeFromNav'] = False
        
        homePagePath_nodes = event.node.getElementsByTagNameNS(ec_namespace,'homePagePath')
        if homePagePath_nodes:
            event.metadata['homePagePath'] = event.reader.getTextValue(homePagePath_nodes[0])

    node = event.node
    manNode = None
    while node.parentNode:
        manNode = node
        node = node.parentNode

    cwsp = manNode.getAttribute("xmlns:cwsp")
    if cwsp == "http://www.dspace.org/xmlns/cwspace_imscp":
        event.metadata['license'] = ["MIT OCW License","MIT OCW License","http://ocw.mit.edu/OcwWeb/Global/terms-of-use.htm","http://ocw.mit.edu/NR/rdonlyres/B2A8B934-D6FD-4481-A702-3C9C6E56A355/0/cc_button.jpg"]


def writeContributeNode(event):
    """ Handle a write contributor node event. """

    cltool = getUtility(IContentLicensingUtility)
    linfo = cltool.getLicenseAndHolderFromObject(event.object)
    if linfo and linfo[0]:
        event.mwriter.createContributeElement(event.writer,
                                              LOM_namespace,
                                              event.node,
                                              'eduCommonsv1.2',
                                              'rights holder',
                                              linfo[0],
                                              event.object.ModificationDate())

    if hasattr(event.object.aq_explicit, 'getInstructorName'):
        instructorName = event.object.getInstructorName()
    else:
        instructorName = None

    if hasattr(event.object.aq_explicit, 'getInstructorEmail'):
        instructorEmail = event.object.getInstructorEmail()
    else:
        instructorEmail = None

    if instructorName:
        event.mwriter.createContributeElement(event.writer,
                                              LOM_namespace,
                                              event.node,
                                              'eduCommonsv1.2',
                                              'Instructor',
                                              instructorName,
                                              event.object.ModificationDate(),
                                              instructorEmail)

def readContributeNode(event):
    """ Handle a read contributor node event. """

    if eduCommons_version == event.source:
        if 'Instructor' == event.value and event.vlist:
            instructorName, instructorEmail = event.vlist[0]
            if instructorName:
                event.metadata['instructorName'] = instructorName
            if instructorEmail:
                event.metadata['instructorEmail'] = instructorEmail
        if 'rights holder' == event.value and event.vlist:
            holderName, holderEmail = event.vlist[0]
            if holderName:
                event.metadata['rightsHolder'] = holderName


def writeOrganizations(event):
    """ Handle write organizations event. """
    
    objects = [obj.getObject() for obj in \
               event.object.portal_catalog.searchResults(
                   path={'query':'/'.join(event.object.getPhysicalPath())+'/',})]

    orgId = event.writer._createPathId(event.object.virtual_url_path(), 'ORG')
    org_node = event.writer._createNode(event.node,
                                        '',
                                        'organization',
                                        attrs=[('identifier', orgId)])

    for obj in objects:
        if not obj.getExcludeFromNav() and 'Course' != obj.portal_type:
            itemId = event.writer._createPathId(obj.virtual_url_path(), 'ITM')
            pathId = event.writer._createPathId(obj.virtual_url_path(), 'RES')
            item_node = event.writer._createNode(org_node,
                                                 '',
                                                 'item',
                                                 attrs=[('identifier', itemId),
                                                        ('identifierref', pathId),
                                                        ('isvisible', 'true'),])
            event.writer._createNode(item_node, '', 'title', obj.title)


def readOrganizations(event):
    """ Handle read organizations event. """

    default = event.node.getAttribute('default')
    organization_nodes = event.node.getElementsByTagName('organization')
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
                event.org[idref] = itemnum
                itemnum += 1

    node = event.node
    manNode = None
    while node.parentNode:
        manNode = node
        node = node.parentNode

    cwsp = manNode.getAttribute("xmlns:cwsp")
    if cwsp == "http://www.dspace.org/xmlns/cwspace_imscp":
        obj = event.object
        clutil = getUtility(IContentLicensingUtility)
        licprops = obj.portal_properties.content_licensing_properties

        if "license_mit" not in clutil.getAvailableLicenses(obj):
            license_mit = ["MIT OCW License","MIT OCW License","http://ocw.mit.edu/OcwWeb/Global/terms-of-use.htm","http://ocw.mit.edu/NR/rdonlyres/B2A8B934-D6FD-4481-A702-3C9C6E56A355/0/cc_button.jpg"]
            licprops.manage_addProperty("license_mit", license_mit, 'lines')
            licprops.manage_changeProperties(SupportedLicenses=list(licprops.SupportedLicenses)+["license_mit"])
            licprops.manage_changeProperties(AvailableLicenses=list(licprops.AvailableLicenses)+["license_mit"])



class eduCommonsCreator:
    """ Set the creator to an eduCommons specific creator function. """

    def __call__(self, event):
        if 'eduCommons' == event.rtype:
            self.createObject(event.object, event.resource, event.data, event.metadata)

    def createObject(self, object, filepath, data, metadata):
        """ Create an object with the given parameters. """
        # Get info
        id = filepath.split('/')[-1]
        
        res_mimetype = mimetypes.guess_type(id)[0]
        
        if not metadata.has_key('Type'):       
            if res_mimetype in ['text/html', 'text/htm' 'text/plain' 'text/x-rst', 'text/structured']:
                metadata['Type'] = 'Document'
            elif res_mimetype == None:
                metadata['Type'] = 'File'
            elif re.match('^image', res_mimetype):
                metadata['Type'] = 'Image'
            else:
                metadata['Type'] = 'File'        

        objtype = metadata['Type']

        # Must check against type for IMS packages that embed the Course Home Page within folder(s)
        # If the check is not in place, eduCommons will try to create a Course object within a Course
        if objtype == 'Course':
            parent = object
        else:
            # Get the ZODB path, create folders if they do not exist
            pathlist = filepath.split('/')
            #pathlist = pathlist[1:]
            parent = object
            for p in pathlist[:-1]:
                newparent = getattr(parent.aq_explicit, p, None)
                if newparent:
                    parent = newparent
                else:
                    parent = self.createFolder(parent, p)
                    parent.title = parent.id

        # Get the new object if it exists, otherwise create it
        newobj = None
        if parent == object and object.portal_type == objtype:
            newobj = object
        elif hasattr(parent.aq_explicit, id):
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

        # If we do not already have an object, create a new oney
        if not newobj:
            parent.invokeFactory(objtype, id)
            newobj = getattr(parent, id)
            newobj = object.portal_factory.doCreate(newobj, id)
            
        # Set the file data on the object
        if objtype in ['Course', 'Document']:
            data = self.stripHeader(data)
            if metadata.has_key('Format'):
                newobj.setText(data, mimetype=metadata['Format'], filename=id)
            else:
                mimetype = mimetypes.guess_type(newobj.absolute_url())[0]
                newobj.setText(data, mimetype=mimetype, filename=id)           
        elif objtype in ['File', 'FSSFile']:
            newobj.setFile(data)
            newobj.setFormat(res_mimetype)
        elif 'Image' == objtype:
            newobj.setImage(data)
            newobj.setFormat(res_mimetype)
        elif 'Link' == objtype:
            doc = minidom.parseString(data)
            anchor_nodes = doc.getElementsByTagName('a')
            if anchor_nodes:
                newobj.setRemoteUrl(str(anchor_nodes[0].getAttribute('href')))

        # Set the metadata on the object
        for key in metadata.keys():
            field = newobj.getField(key)
            if field:
                mutator = field.getMutator(newobj)
                if mutator:
                    field = metadata[key]
                    mutator(field)

        if metadata.has_key('accessible'):
            IAnnotations(newobj)['eduCommons.accessible'] = metadata['accessible']
        else:
            IAnnotations(newobj)['eduCommons.accessible'] = False

        if objtype == 'Course':
            newobj.setExcludeFromNav('False')

        if metadata.has_key('rightsHolder'):
            getUtility(IContentLicensingUtility).setRightsHolder(newobj, metadata['rightsHolder'])

        if metadata.has_key('license'):
            getUtility(IContentLicensingUtility).setRightsLicense(newobj, metadata['license'])

        if metadata.has_key('homePagePath'):
            course = getUtility(IECUtility).FindECParent(newobj)
            if course.portal_type == 'Course':
                if course.hasProperty('homePagePath'):
                    course.manage_changeProperties(homePagePath=metadata['homePagePath'])
                else:
                    course.manage_addProperty('homePagePath',metadata['homePagePath'],'string')

        # Reindex the object so that the new stuff appears
        newobj.reindexObject()


    def createFolder(self, parent, id):
        """ Create an object """

        #hack to avoid IMS import failures from MIT package
        if 'search' == id:
            id = '%s-1' %id

        parent.invokeFactory('Folder',id)
        obj = getattr(parent, id)
        obj.setExcludeFromNav(True)
        obj = obj.portal_factory.doCreate(obj, id)
        obj.reindexObject()

        return obj


    def stripHeader(self, data):
        """ Tidy up any html, if we can. """
        # get the body text
        result = RE_BODY.search(data)
        if result:
            data = result.group(1)
        return data
            

eduCommonsCreateObject = eduCommonsCreator()
 

def syndicateFolderishObject(object, event):
    """ Enable RSS feed upon FolderishObject creation. """
    if not hasattr(object.aq_explicit, 'syndication_information'):
        syInfo = SyndicationInformation()
        object._setObject('syndication_information', syInfo)
        portal = object.portal_url.getPortalObject()
        portal_syn = portal.portal_syndication
        syInfo = object._getOb('syndication_information')
        syInfo.syUpdatePeriod = portal_syn.syUpdatePeriod
        syInfo.syUpdateFrequency = portal_syn.syUpdateFrequency
        syInfo.syUpdateBase = portal_syn.syUpdateBase
        syInfo.max_items = portal_syn.max_items
        syInfo.description = "Channel Description"

def addObjPosition(object, event):
    appendObjPosition(object)

def appendObjPosition(object):
    if not object.isTemporary():
        ecutil = queryUtility(IECUtility)
        if ecutil:
            parent = ecutil.FindECParent(object)
            if parent.Type() == 'Course':
                path = {'path':{'query':'/'.join(parent.getPhysicalPath())+'/'},}
                brains = object.portal_catalog.searchResults(path)
                if brains:
                    pos = [0,]
                    for brain in brains:
                        obj = brain.getObject()
                        annotations = IAnnotations(obj)
                        if annotations.has_key('eduCommons.objPositionInCourse'):
                            pos += [annotations['eduCommons.objPositionInCourse'],]
                    maxpos = max(pos)
                    if maxpos > 0:
                        maxpos += 1
                    else:
                        maxpos = 1
                else:
                    maxpos = 1
                
                annotations = IAnnotations(object)
                annotations['eduCommons.objPositionInCourse'] = maxpos

                zipobj = getattr(parent, parent.id + '.zip', None)
                if zipobj:
                    IAnnotations(zipobj)['eduCommons.objPositionInCourse'] = maxpos + 1
                    zipobj.reindexObject()
                    
    

class eduCommonsImportForm(ImportForm):
    """ Render the import form  """

    @action('Upload')
    def action_import(self, action, data):

        filename = self.context.REQUEST['form.filename']
        packagetype = self.context.REQUEST['form.packagetype']

        imsvocab = getUtility(IVocabularyFactory, name='imsvocab')(self.context)
        package_xform = imsvocab.getTermByToken(packagetype).value

        self.ims_util.importZipfile(self.context,filename,package_xform,rtype='eduCommons')

        self.request.response.redirect('.')



def updateZipDownload(object, event):
    """ Check for factors related to editing and adding objects """
    pw = event.object.portal_workflow

    if pw.getInfoFor(event.object,'review_state') == 'Published':
        validateContext(object, event)

    

def ZipFileMaker(event):
    """ Handler for creating zip download for objects that are moving through workflow changes """

    if event.bulkChange and event.target in ['manager_rework','retract']:
        validateContext(event.object,event)        
    elif event.initial_state == 'Published' or event.target == 'publish':
        validateContext(event.object,event)
    else:
        pass 

def deleteObjectHandler(event):
    """ Handlet the delete object event """
    if event.bulkChange == True:
        if event.contains_published:
            validateContext(event.object, event)
    else:
        validateContext(event.object, event)


def validateContext(object, event):
    """ create the Zipfile after some final checks """

    parent = getUtility(IECUtility).FindECParent(object)
    file_id = parent.id + '.zip'
    pw = event.object.portal_workflow
    
    if parent.portal_type == 'Course':
        if pw.getInfoFor(parent,'review_state') == 'Published':
            if not event.object.isTemporary():
                if event.object.id != file_id:
                    if not IContainerModifiedEvent.providedBy(event):
                        ZipFileCreator(parent,event).createZipFile()




## Deprecated for 3.1.0, as auto generated Course packages have been disabled
## Replaced by Package Course functionality :: browser/packagecourseview.py
class ZipFileCreator:

    def __init__(self, object, event):
        self.obj = object
        self.event = event

    def createZipFile(self):
        """ Create a zip file for when the file is modified. """

        course = self.obj
        file_id = course.id + '.zip'

        pm = course.portal_membership
        user_id = pm.getAuthenticatedMember().id
        roles = pm.getAuthenticatedMember().getRoles()
        if 'Publisher' in roles:
            roles += ['Administrator']
            course.manage_setLocalRoles(user_id, roles)
            course.reindexObjectSecurity()

        data = self.getZipFileData(course=course)

        if not data:
            return

        if not hasattr(course,file_id):
                    
            course.invokeFactory("File",file_id)
            fileobj = getattr(course,file_id)
            fileobj.content_status_modify(workflow_action='submit')
            fileobj.content_status_modify(workflow_action='release')
            fileobj.content_status_modify(workflow_action='publish')
            fileobj.setTitle("Download This Course")

        else:
            fileobj = getattr(course,file_id)            
            fileobj.setTitle("Download This Course")

        
        fileobj.setExcludeFromNav(False)
        fileobj.setFile(data)
        appendObjPosition(fileobj)

        course.portal_catalog.reindexObject(fileobj)
        user_ids = []
        user_ids += [user_id]
        course.manage_delLocalRoles(userids=user_ids)
        course.reindexObjectSecurity()

    def getZipFileData(self, course, obj_paths=[], filename=None):
        """
        Return the content for a zip file
        """
        objects_list = getUtility(IZipFileTransportUtility)._createObjectList(course, obj_paths, state=['Published'])
        objects_list.insert(0,course)
        context_path = str( course.virtual_url_path() )

        # Do not include the zip file for the course
        mod_objects_list = [object for object in objects_list if object.virtual_url_path().replace(course.virtual_url_path(),'') != '/' + course.id + '.zip']
        
        if mod_objects_list:
            content = getUtility(IZipFileTransportUtility)._getAllObjectsData(mod_objects_list, context_path)
            return content
        else:
            return None

