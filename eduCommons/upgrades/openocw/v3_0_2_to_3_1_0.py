from Products.CMFPlone.utils import _createObjectByType
from StringIO import StringIO
import string
from zope.component import getUtility, getMultiAdapter
from Products.CMFPlone.factory import addPloneSite
from Products.CMFCore.utils import getToolByName
from Products.eduCommons import portlet
from Products.eduCommons.browser.packagecourseview import appendObjPosition
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
from Products.CMFCore.ActionInformation import Action


def migrate(portal_setup):
    """ Migration from eduCommons 3.0.2 to 3.1.0  """

    portal_url = getToolByName(portal_setup, 'portal_url')
    portal=  portal_url.getPortalObject()

    updateTransforms(portal)
    updateKupu(portal)
    createAccessibilityGuidelines(portal)
    updateSettings(portal)
    updateActions(portal)
    updateCourses(portal)
    disableKSS(portal)

def updateTransforms(portal):
    """ Update safe_html portal_transform  """
    from Products.CMFDefault.utils import VALID_TAGS
    from Products.CMFDefault.utils import NASTY_TAGS

    valid_tags = VALID_TAGS.copy()
    nasty_tags = NASTY_TAGS.copy()
    
    nasty_tags.pop('applet')
    nasty_tags.pop('embed')
    nasty_tags.pop('object')
    nasty_tags.pop('script')

    valid_tags['applet'] = 1
    valid_tags['embed'] = 1
    valid_tags['object'] = 1
    valid_tags['thead'] = 1
    valid_tags['tfoot'] = 1
    valid_tags['param'] = 0

    kwargs = {'nasty_tags': nasty_tags,
              'valid_tags': valid_tags,
              'remove_javascript': 0}
    
    transform = getattr(getToolByName(portal, 'portal_transforms'), 'safe_html')
            
    for k in list(kwargs):
        if isinstance(kwargs[k], dict):
            v = kwargs[k]
            kwargs[k+'_key'] = v.keys()
            kwargs[k+'_value'] = [str(s) for s in v.values()]
            del kwargs[k]

    transform.set_parameters(**kwargs)

def updateKupu(portal):
    """ update kupu default settings  """ 
    kupu_tool = getToolByName(portal, 'kupu_library_tool')
    
    combos = []

    #enable original size images
    kupu_tool.allowOriginalImageSize = True

    #remove default stripped combo in kupu
    kupu_tool.set_stripped_combinations(combos)

    #link using UIDs
    kupu_tool.linkbyuid = True

    #Allow captioned images
    kupu_tool.captioning = True

    #Add eduCommons documentTable style
    kupu_tool.table_classnames += ['documentTable|eduCommons Content']

    #Make undo/redo buttons visible
    kupu_tool._setToolbarFilters([{'id': 'bg-undo', 'override': '', 'visible': 1}, 
                                  {'id': 'undo-button', 'override': '', 'visible': 1}, 
                                  {'id': 'redo-button', 'override': '', 'visible': 1},
                                  {'id': 'embed-tab', 'override': '', 'visible': 1},],
                                  '')

    #Remove image_preview class from embedded images
    kupu_tool.updatePreviewActions([{'classes': '', 'defscale': '', 'expression': 'string:${object_url}/image_thumb', 'marker': 'x', 'mediatype': 'image', 'normal': '', 'portal_type': 'Image', 'scalefield': 'image'}, 
                                    {'classes': '', 'defscale': 'image_preview', 'expression': 'string:${object_url}/image_thumb', 'marker': 'x', 'mediatype': 'image', 'normal': '', 'portal_type': 'News Item', 'scalefield': 'image'}, 
                                    {'classes': '', 'defscale': 'image_preview', 'expression': '', 'marker': '-', 'mediatype': 'image', 'normal': '', 'portal_type': '', 'scalefield': 'image'}])

    
    #remove cellpadding, cellspacing, bgcolor from sripped attrs list
    attrs_to_remove = ['cellpadding', 'cellspacing', 'bgcolor']
    stripped_attributes = kupu_tool.get_stripped_attributes()
    for attr in attrs_to_remove:
        if attr in stripped_attributes:
            stripped_attributes.remove(attr)
            
    kupu_tool.set_stripped_attributes(stripped_attributes)

def createAccessibilityGuidelines(portal):
    """ create accessibility guidelines page """
    if hasattr(portal, 'help'):
        help = getattr(portal, 'help')
        _createObjectByType('Document', help, id="accessibility-guidelines", 
                            title="Accessibility Guidelines",
                            description='Guidelines to help determine if content meets accessibility standards.')
        context = getattr(portal.help, 'accessibility-guidelines')
        publishObject(context)
        template = '@@accessibilityguidelines_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

def updateSettings(portal):
    """ update various portal settings  """

    #Check Mail Host Title
    if '' == portal.MailHost.title:
        portal.MailHost = 'Plone Mail Host'

    #Fix RSS max_items
    portal.portal_syndication.max_items = 999

    #update courselist RSS max_items
    if hasattr(portal, 'courselist'):
        portal.courselist.syndication_information.max_items = 999

    #update max_items on each Department
    div_brains =  portal.portal_catalog(path= {'query':'/'.join(portal.getPhysicalPath())+'/'}, portal_type='Division')
    for div in div_brains:
        div = div.getObject()
        if hasattr(div, 'syndication_information'):
            div.syndication_information.max_items = 999

    #update max_items on each Course
    course_brains =  portal.portal_catalog(path= {'query':'/'.join(portal.getPhysicalPath())+'/'}, portal_type='Course')
    for course in course_brains:
        course = course.getObject()
        if hasattr(course, 'syndication_information'):
            course.syndication_information.max_items = 999

    #set portal to openOCW in educommons_properties
    ec_props = portal.portal_properties.educommons_properties
    ec_props.manage_addProperty(id='reusecourse_enabled', type='boolean', value='True')
    ec_props.manage_addProperty(id='reusecourse_instance', type='string', value='http://openocw.org')

    #create FSSFile Type
    types_tool = portal.portal_types
    types_tool.manage_addTypeInformation(DynamicViewTypeInformation.meta_type, id='FSSFile', typeinfo_name='FSSFile')    
    FSSFile = types_tool.FSSFile
    FSSFile.description = 'An external file uploaded to the site which uses FileSystemStorage'    
    FSSFile.title = 'FSSFile'
    FSSFile.content_icon = 'file_icon.gif'
    FSSFile.content_meta_type = 'FSSFile'
    FSSFile.product = 'Products.eduCommons'
    FSSFile.factory = 'addFSSFile'
    FSSFile.immediate_view = 'file_view'
    FSSFile.default_view = 'file_view'
    FSSFile.view_methods = ('file_view',)

    wf_tool = portal.portal_workflow
    wf_tool.setChainForPortalTypes(('FSSFile',), 'two_step_workflow')

    #allow FSSFile for courses
    portal.portal_types.Course.manage_changeProperties(allowed_content_types=('File', 'FSSFile', 'Image', 'Document', 'Link', 'Folder'))   


def updateActions(portal):
    """ Add the Package Course folder_button action  """
    at = portal.portal_actions

    pkg_action  = Action('package_course',
                         title = 'Package Course',
                         descriptiong = '',
                         url_expr = 'string:@@package_course_view:method',
                         available_expr = "python:object.Type() == 'Course' and object.portal_workflow.getInfoFor(object, 'review_state') == 'Published'",
                         permissions = 'Modify portal content',
                         visible = 1)

    folder_buttons = at['folder_buttons']
    folder_buttons._setObject('package_course', pkg_action)


def updateCourses(portal):
    """ Migrate current courses in ZODB  """

    course_brains =  portal.portal_catalog(path= {'query':'/'.join(portal.getPhysicalPath())+'/'}, portal_type='Course')
    
    for course in course_brains:  
        course = course.getObject()

        #add reuse course portlet to existent courses
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=course)
        right = getMultiAdapter((portal, rightColumn), IPortletAssignmentMapping, context=course)

        if u'Reuse Course' not in right.keys():
            right[u'Reuse Course'] = portlet.reusecourseportlet.Assignment()

        #add crosslisting field to existent courses
        crosslisting = course.Schema()['crosslisting']
        crosslisting.set(course, (''))

        #repackage Download this Course object for existent courses
        zip_exists = 0
        for object in course.listFolderContents():
            if 'download this course' == string.lower(object.Title()):
                #delete object, repackage as FSS based IMS package
                zip_exists = 1
                course.manage_delObjects([object.getId()])

        #commenting out for now, too fragile for all potential courses.
        #Will have to hand package courses post migration
        if zip_exists == 1:
            file_id = course.id + '.zip'

            ims_util = getUtility(IIMSTransportUtility)
            data, file_id = ims_util.exportZipfile(course, file_id)

            course.invokeFactory("FSSFile",id=file_id, title="Download this Course")
            fileobj = getattr(course,file_id)
            publishObject(fileobj)
            fileobj.setTitle("Download This Course")
            
            fileobj.setExcludeFromNav(True)
            fileobj.setFile(data)
            appendObjPosition(fileobj)

            course.portal_catalog.reindexObject(fileobj)

def publishObject(context):
    """ Move an object into the published state """
    wftool =  getToolByName(context, 'portal_workflow')

    if wftool.getInfoFor(context, 'review_state') != 'Published':
        wftool.doActionFor(context, 'publish')        

def disableKSS(context):
    """ Disable KSS/inline edits """
    kss = context.portal_kss

    kss.getResource('at.kss').setEnabled(False)
    kss.getResource('plone.kss').setEnabled(False)





