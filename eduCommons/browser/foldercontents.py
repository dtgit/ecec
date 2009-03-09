
from zope.component import getMultiAdapter
from zope.interface import implements

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from plone.memoize import instance
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.tableview import Table
from kss.core import KSSView
from zope.component import getUtility
from Products.eduCommons.utilities.interfaces import IECUtility

from Products.CMFPlone.interfaces import IPloneSiteRoot

from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.content.batching import Batch
from plone.memoize import instance

from plone.app.content.browser.foldercontents import FolderContentsTable as DefaultTable
from plone.app.content.browser.foldercontents import FolderContentsView as DefaultView

from zope.annotation import IAnnotations

import urllib

NOT_ADDABLE_TYPES = ('Favorite',)

class OrderContentsView(DefaultView):
    """
    """
    
    def contents_table(self):
	parent = getUtility(IECUtility).FindECParent(self.context)
        table = OrderContentsTable(self.context, self.request, contentFilter={'path':{'query':'/'.join(parent.getPhysicalPath())+'/'},'getExcludeFromNav':False,'sort_on':'getObjPositionInCourse'})
        return table.render()


class OrderContentsTable(DefaultTable):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = self.context.absolute_url()
        view_url = url + '/@@order_courseobjs'
        self.table = OrderTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    @property
    @instance.memoize
    def items(self):
        """
        """
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = self.context.browserDefault()
                
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.portal_catalog.searchResults
	
        results = []

        brains = self.context.portal_catalog.searchResults(self.contentFilter)

        i = 0
        for obj in [brain for brain in brains if not getattr(brain.aq_explicit, 'exclude_from_nav', True) and brain.portal_type != 'Course']:

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"
            
            if getattr(obj.aq_explicit, 'exclude_from_nav', True):
                continue

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
                                
            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = self.context.isExpired(obj),
            ))

            i += 1

        return results

    @property
    def buttons(self):
        buttons = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] not in ['paste','cut','copy','import']:
                buttons.append(self.setbuttonclass(button))
        return buttons



class OrderTable(Table):
    """   
    The table renders a table with sortable columns etc.

    It is meant to be subclassed to provide methods for getting specific table info.
    """                
    @property
    @instance.memoize
    def batch(self):
        ba = Batch(self.items,pagesize=len(self.items),)
        map(self.set_checked, ba)
        return ba

    render = ViewPageTemplateFile("table.pt")




class FolderContentsCCView(DefaultView):
    """
    """
    def contents_table(self):
        table = FolderContentsCCTable(self.context, self.request)
        return table.render()



class FolderContentsCCTable(DefaultTable):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = self.context.absolute_url()
        view_url = url + '/folder_contents'
        self.table = CCTable(request, url, view_url, self.items,
                           show_sort_column=0,
                           buttons=self.buttons)

    @property
    @instance.memoize
    def items(self):
        """
        """
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = self.context.browserDefault()
                
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents
	
        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
            #Refactor :: determine why ProxyIndex not accessible here
            if IAnnotations(obj.getObject()).has_key('eduCommons.clearcopyright'):
                cc_status = IAnnotations(obj.getObject())['eduCommons.clearcopyright']
            else:
                cc_status = False

            if IAnnotations(obj.getObject()).has_key('eduCommons.accessible'):
                accessibility_status = IAnnotations(obj.getObject())['eduCommons.accessible']
            else:
                accessibility_status = False

            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = self.context.isExpired(obj),
                #Refactor :: determine why ProxyIndex not accessible here
                cc_status = cc_status,
                accessibility_status = accessibility_status
            ))
        return results



class CCTable(Table):
    """   
    The table renders a table with sortable columns etc.

    It is meant to be subclassed to provide methods for getting specific table info.
    """                
    render = ViewPageTemplateFile("cc_table.pt")

class FolderContentsCCKSSView(KSSView):
    def update_table(self, pagenumber='1', sort_on='getObjPositionInCourse'):
        self.request.set('sort_on', sort_on)
        self.request.set('pagenumber', pagenumber)
        table = FolderContentsCCTable(self.context, self.request,
                                    contentFilter={'sort_on':sort_on})
        return self.replace_table(table)

    def replace_table(self, table):
        core = self.getCommandSet('core')
        core.replaceInnerHTML('#folderlisting-main-table', table.render())
        return self.render()

