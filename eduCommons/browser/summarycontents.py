from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
import urllib
from zope.component import getUtility
from Products.eduCommons.utilities.interfaces import IECUtility
from plone.app.content.browser.tableview import Table
from kss.core import KSSView
from zope.app.pagetemplate import ViewPageTemplateFile
from Acquisition import aq_parent, aq_inner
from zope.annotation import IAnnotations



class SummaryContentsView(FolderContentsView):
    """
    Override contents table to use FindECParent and use SummaryContentsTable
    """

    def contents_table(self):
	ecutil = getUtility(IECUtility)
	parent = ecutil.FindECParent(self.context)
        path = '/'.join(parent.getPhysicalPath())
        request = self.request
        if request.has_key('state'):
            review_state = request['state']
	else:
	    review_state = ''
        table = SummaryContentsTable(parent, self.request, contentFilter={'path':path,'review_state':review_state})
        return table.render()


class SummaryContentsTable(FolderContentsTable):
    """   
    The foldercontents table renders the table and its actions.
    """                


    def __init__(self, context, request, contentFilter={}):
        """
        Initialize the table
        """
        super(SummaryContentsTable, self).__init__(context, request, contentFilter)

        url = self.context.absolute_url()
        view_url = url + '/summary_contents'
        self.table = SummaryTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    @property
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
       

        contentsMethod = self.context.queryCatalog
       
        results = list()
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if i % 2 == 0:
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

            if IAnnotations(obj.getObject()).has_key('eduCommons.clearcopyright'):
                cc_status = IAnnotations(obj.getObject())['eduCommons.clearcopyright']
            else:
                cc_status = False
                              
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
                cc_status = cc_status,
            ))
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

class SummaryTable(Table):
    """
    The table renders a table that is 

    the summary portlet.

    """    

    render = ViewPageTemplateFile("summary_table.pt")
    batching = ViewPageTemplateFile("summary_batching.pt")

class SummaryContentsKSSView(KSSView):
    def update_table(self, pagenumber='1', sort_on='getObjPositionInCourse'):
        self.request.set('sort_on', sort_on)
        self.request.set('pagenumber', pagenumber)
        table = SummaryContentsTable(self.context, self.request,
                                    contentFilter={'sort_on':sort_on})
        return self.replace_table(table)
