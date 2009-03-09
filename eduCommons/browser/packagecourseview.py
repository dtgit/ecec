from zope.publisher.browser import BrowserView
from Products.CMFPlone import PloneMessageFactory as _
from zope.component import getUtility, queryUtility
from Products.ZipFileTransport.utilities.interfaces import IZipFileTransportUtility
from zope.annotation.interfaces import IAnnotations
from Products.eduCommons.utilities.interfaces import IECUtility
from Products.CMFCore.utils import getToolByName

from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility


    
class PackageCourseView(BrowserView):
    """View to package a published course """

    def __call__(self):
        self.createIMSFile()
        message = _('Course has been packaged')
        url = '%s/folder_contents' % self.context.absolute_url()
        self.context.plone_utils.addPortalMessage(message)
        self.request.response.redirect(url)


    def createIMSFile(self):
        """ Package a Published Course. """

        course = self.context
        file_id = course.id + '.zip'

        pm = course.portal_membership
        user_id = pm.getAuthenticatedMember().id
        roles = pm.getAuthenticatedMember().getRoles()
        if 'Publisher' in roles:
            roles += ['Administrator']
            course.manage_setLocalRoles(user_id, roles)
            course.reindexObjectSecurity()

        #this needs to fire off IMS packaging instead of zip
        ims_util = getUtility(IIMSTransportUtility)
        data, file_id= ims_util.exportZipfile(course,file_id)

        if not hasattr(course,file_id):
            course.invokeFactory("FSSFile",id=file_id, title="Download this Course")
            fileobj = getattr(course,file_id)
            wftool = getToolByName(fileobj, 'portal_workflow')
            wftool.doActionFor(fileobj, 'submit')
            wftool.doActionFor(fileobj, 'release')
            wftool.doActionFor(fileobj, 'publish')        
            fileobj.setTitle("Download This Course")
        else:
            fileobj = getattr(course,file_id)            
            fileobj.setTitle("Download This Course")
        
        fileobj.setExcludeFromNav(True)
        fileobj.setFile(data)
        appendObjPosition(fileobj)

        course.portal_catalog.reindexObject(fileobj)
        user_ids = []
        user_ids += [user_id]
        course.manage_delLocalRoles(userids=user_ids)
        course.reindexObjectSecurity()




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
