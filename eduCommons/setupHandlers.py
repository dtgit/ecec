from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.eduCommons import portlet
from utilities.interfaces import IECUtility
from utilities.utils import eduCommonsUtility
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from Products.Five.site.localsite import enableLocalSiteHook
from zope.component import getSiteManager
from eventHandlers import syndicateFolderishObject
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations
from Products.ProxyIndex import ProxyIndex


# setup handlers for eduCommons

def importFinalSteps(context):
    site = context.getSite()
    setupDefaultPortlets(site)
    defaultSettings(site)
    setupUtilities(site)
    setupControlPanel(site)
    setupTransforms(site)
    setupKupu(site)
    customizeAddOnProducts(site)
    addCopyrightIndexToCatalog(site)
    addCopyrightMetadataToCatalog(site)
    addAccessibilityIndexToCatalog(site)
    addAccessibilityMetadataToCatalog(site)
    addObjPositionIndexToCatalog(site)
    addObjPositionMetadataToCatalog(site)

def importContent(context):
    site = context.getSite()
    if getattr(site, 'REQUEST', None):
        if site.REQUEST.has_key('title'):
            site.setTitle(site.REQUEST['title'])
    setupPortalContent(site)

def setupUtilities(site):
    """ Register a local utility """

    if not ISite.providedBy(site):
        enableLocalSiteHook(site)

    setSite(site)

    sm = getSiteManager()
    if not sm.queryUtility(IECUtility):
        sm.registerUtility(eduCommonsUtility('educommonsutility'),
                        IECUtility)

def setupControlPanel(site):
    """ Tweak Control Panel conditions  """
    from Products.CMFCore.Expression import Expression
    control_panel = site.portal_controlpanel

    panels = ['ZMI', 'NavigationSettings', 'QuickInstaller', 'TypesSettings', 'portal_atct', 'errorLog']
    actions = control_panel.listActions()

    for panel in panels:
        for action in actions:
            if panel == action.id:
                action.condition = Expression('python:"Manager" in here.portal_membership.getAuthenticatedMember().getRoles()')

def setupTransforms(portal):
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

def setupKupu(portal):
    kupu_tool = getToolByName(portal, 'kupu_library_tool')
    
    combos = []

    #enable original size images
    kupu_tool.allowOriginalImageSize = True

    #remove default stripped combo in kupu
    kupu_tool.set_stripped_combinations(combos)

    #Remove image_preview class from embedded images
    kupu_tool.updatePreviewActions([{'classes': '', 'defscale': '', 'expression': 'string:${object_url}/image_thumb', 'marker': 'x', 'mediatype': 'image', 'normal': '', 'portal_type': 'Image', 'scalefield': 'image'}, 
                                    {'classes': '', 'defscale': 'image_preview', 'expression': 'string:${object_url}/image_thumb', 'marker': 'x', 'mediatype': 'image', 'normal': '', 'portal_type': 'News Item', 'scalefield': 'image'}, 
                                    {'classes': '', 'defscale': 'image_preview', 'expression': '', 'marker': '-', 'mediatype': 'image', 'normal': '', 'portal_type': '', 'scalefield': 'image'}])



def setupPortalContent(portal):
    """ Setup default eduCommons content """

    existing = portal.objectIds()
    wftool = getToolByName(portal, 'portal_workflow')

    syndicateFolderishObject(portal, event=None)

    # If Members, news, and/or event objects exist, remove them
    delobjs = []
    if 'Members' in existing:
        delobjs.append('Members')
    if 'news' in existing:
        delobjs.append('news')
    if 'events' in existing:
        delobjs.append('events')
    if delobjs:
        portal.manage_delObjects(delobjs)

    # Add the Course List
    if 'courselist' not in existing:
        # Create a new course list
        _createObjectByType('CoursesTopic', portal, id='courselist', title='Courses',
                            description='A list of courses on this site.')
        courselist = portal.courselist
        # Set the criterion for the course list smart folder
        crit = courselist.addCriterion('Type', 'ATPortalTypeCriterion')
        crit.setValue('Division')
        courselist.setSortCriterion('sortable_title', reversed=False)
        courselist.setLayout('courses_listing')
        # publish it
        if wftool.getInfoFor(courselist, 'review_state') != 'published':
            wftool.doActionFor(courselist, 'publish')


    fptitle = 'Welcome to eduCommons'
    fpdesc = 'eduCommons provides access to educational materials more commonly known as OpenCourseWare.'
    if 'front-page' not in existing:
        _createObjectByType('Document', portal,id='front-page', title=fptitle,
                            description=fpdesc)
    context = portal.get('front-page')
    context.setTitle(fptitle)
    context.setDescription(fpdesc)
    template = '@@frontpage_view'
    # Need try/except for QuickInstaller installations of 3rd party products
    try:
        template = context.restrictedTraverse(str(template))       
        text = template(context)
        context.setText(text)
        publishObject(context)
    except AttributeError:
        pass

    # Add About
    if 'about' not in existing:
        _createObjectByType('Folder', portal, id='about', title='About OCW',
                            description='Current information about the eduCommons install on this web site.')
        about = portal.about
        publishObject(about)
        _createObjectByType('Document',about,id='abouttext_text',title='About OCW',description='About')
        context = portal.about.abouttext_text
        
        publishObject(about.abouttext_text)
        template = '@@abouttext_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)
        context.setPresentation(True)

        about.setDefaultPage('abouttext_text')

        #Terms of Use
        _createObjectByType('Document', about, id="terms-of-use", title="Terms of Use", 
                            description='Terms of use for this web site.')
        context = getattr(portal.about, 'terms-of-use')
        publishObject(context)
        template = '@@tou_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

        #Privacy Policy
        _createObjectByType('Document', about, id="privacy-policy", title="Privacy Policy", 
                            description='The privacy policy for this web site.')
        context = getattr(portal.about, 'privacy-policy')
        publishObject(context)
        template = '@@privacypolicy_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

        

    # Add Help
    if 'help' not in existing:
        _createObjectByType('Folder', portal, id='help', title='Help',
                            description='Help')
        help = portal.help
        publishObject(help)

        _createObjectByType('Document',help,id='help_text',title='Help',description='Help')
        context = portal.help.help_text

        publishObject(context)
        template = '@@faq_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)
        context.setTableContents(True)
        
        help.setDefaultPage('help_text')

        #Accessibility Guidelines
        _createObjectByType('Document', help, id="accessibility-guidelines", 
                            title="Accessibility Guidelines",
                            description='Guidelines to help determine if content meets accessibility standards.')
        context = getattr(portal.help, 'accessibility-guidelines')
        publishObject(context)
        template = '@@accessibilityguidelines_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

    # Add Feedback
    if 'feedback' not in existing:
        _createObjectByType('Feedback', portal, id='feedback', title='Feedback',
                            description='Feedback')
        feedback = portal.feedback        
        publishObject(feedback)
        feedback.setLayout('feedback_view')

        _createObjectByType('Document', feedback, id='thanks', title='Thank You',
                            description='')
        feedback.thanks.setText('Thank you for your feedback.')
        feedback.thanks.setExcludeFromNav(True)
        publishObject(feedback.thanks)
        feedback.thanks.reindexObject()
 
def publishObject(context):
    """ Move an object into the published state """
    wftool =  getToolByName(context, 'portal_workflow')


    if wftool.getInfoFor(context, 'review_state') != 'Published':
        wftool.doActionFor(context, 'submit')
        wftool.doActionFor(context, 'release')
        wftool.doActionFor(context, 'publish')        

           
        
def setupDefaultPortlets(portal):
    """ Setup default portlets for eduCommons """

    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    left = getMultiAdapter((portal, leftColumn), IPortletAssignmentMapping, context=portal)

    # Add the eduCommons custom simple navigation portlet
    if u'Simple Nav Portlet' not in left:
        left[u'Simple Nav Portlet'] = portlet.simplenavportlet.Assignment()

    # Turn off other left hand portlets
    if u'navigation' in left:
        del left[u'navigation']
    if u'login' in left:
        del left[u'login']
    if u'recent' in left:
        del left[u'recent']

    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
    right = getMultiAdapter((portal, rightColumn), IPortletAssignmentMapping, context=portal)

    if u'Course Builder Portlet' not in right:
        right[u'Course Builder Portlet'] = portlet.coursebuilder.Assignment()

    # Turn off right hand portlets
    if u'review' in right:
        del right[u'review']

    if u'news' in right:
        del right[u'news']

    if u'events' in right:
        del right[u'events']

    if u'calendar' in right:
        del right[u'calendar']

def defaultSettings(portal):
    """ Miscellaneous settings  """

    # Change allow_content_types for Site
    pt = portal.portal_types
    site = getattr(pt, 'Plone Site')
    site.filter_content_types = 1
    site.allowed_content_types = ('Topic', 'Division', 'Folder', 'Document', 'Link', 'File', 'Image', 'CoursesTopic', 'Feedback')


    # Give the MailHost a Title
    mailhost = getattr(site, 'MailHost')
    mailhost.title = 'Plone Mail Host'
    
    # Change allow_content_types for Folder
    # Modifying it in setuphandlers allows us to maintain one less content type
    folder = getattr(pt, 'Folder')
    folder.filter_content_types = 1
    folder.allowed_content_types = ('FSSFile','Folder', 'Document', 'Link', 'File', 'Image')

    # Update default types for Wiki Behaviour
    import plone
    wicked_type_regs = {'Page': plone.app.controlpanel.markup.wicked_type_regs['Page']}
    plone.app.controlpanel.markup.wicked_type_regs = wicked_type_regs

    portal.portal_properties.educommons_properties.division_descriptor = 'Departments'

    #Update Sitewide Default Syndication Properties
    portal.portal_syndication.max_items = 999

def customizeAddOnProducts(portal):
    """ Customizations to dependent products  """

    #Move PloneBookmarklets document actions to bottom of the list
    dactions = portal.portal_actions.document_actions
    if 'bookmarklets' in dactions:
        dactions.moveObjectsToBottom(('bookmarklets',))


def copyrightClearedOnObj_value(object, portal, **kwargs):
    try:
        copyright = IAnnotations(object)
 	return copyright['eduCommons.clearcopyright']
    except (ComponentLookupError, TypeError, ValueError, KeyError):
 	# The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('copyrightClearedOnObj', copyrightClearedOnObj_value)


def addCopyrightIndexToCatalog(portal,
                             indexes=('copyrightClearedOnObj',),
                             catalog='portal_catalog'):
    """Adds the specified indices as FieldIndexes to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for index in indexes:
            if index in cat.indexes():
                continue
            ProxyIndex.manage_addProxyIndex(portal.portal_catalog, 
                                            index, 
                                            idx_type='FieldIndex', 
                                            value_expr='object/search_view/copyrightClearedOnObj')
            reindex.append(index)
        if reindex:
            cat.manage_reindexIndex(reindex)

def addCopyrightMetadataToCatalog(portal,
                             metadata=('copyrightClearedOnObj',),
                             catalog='portal_catalog'):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for column in metadata:
            if column in cat.schema():
                continue
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()

def addAccessibilityIndexToCatalog(portal,
                             indexes=('AccessibilitySetOnObj',),
                             catalog='portal_catalog'):
    """Adds the specified indices as FieldIndexes to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for index in indexes:
            if index in cat.indexes():
                continue
            ProxyIndex.manage_addProxyIndex(portal.portal_catalog, 
                                            index, 
                                            idx_type='FieldIndex', 
                                            value_expr='object/search_view/AccessibilitySetOnObj')
            reindex.append(index)
        if reindex:
            cat.manage_reindexIndex(reindex)

def addAccessibilityMetadataToCatalog(portal,
                             metadata=('AccessibilitySetOnObj',),
                             catalog='portal_catalog'):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for column in metadata:
            if column in cat.schema():
                continue
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()


def getObjPositionInCourse_value(object, portal, **kwargs):
    try:
        copyright = IAnnotations(object)
 	return copyright['eduCommons.objPositionInCourse']
    except (ComponentLookupError, TypeError, ValueError, KeyError):
 	# The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('getObjPositionInCourse', getObjPositionInCourse_value)


def addObjPositionIndexToCatalog(portal,
                             indexes=('getObjPositionInCourse',),
                             catalog='portal_catalog'):
    """Adds the specified indices as FieldIndexes to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for index in indexes:
            if index in cat.indexes():
                continue
            ProxyIndex.manage_addProxyIndex(portal.portal_catalog, 
                                            index, 
                                            idx_type='FieldIndex', 
                                            value_expr='object/search_view/getObjPositionInCourse')

            reindex.append(index)
        if reindex:
            cat.manage_reindexIndex(reindex)

def addObjPositionMetadataToCatalog(portal,
                             metadata=('getObjPositionInCourse',),
                             catalog='portal_catalog'):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for column in metadata:
            if column in cat.schema():
                continue
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()

    
