from urllib import quote_plus

from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter, getAdapters, queryUtility
from zope.app.component.hooks import getSite

from zope.component.interfaces import IFactory
from zope.i18n import translate
from zope.app.container.constraints import checkFactory
from zope.app.publisher.interfaces.browser import AddMenu

from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.interfaces import IWorkflowSubMenuItem

from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IWorkflowMenu

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils

class TemplatesSubMenuItem(BrowserSubMenuItem):
    implements(IActionsSubMenuItem)
    
    title = _(u'label_template_menu', default=u'Apply Template')
    description = _(u'title_template_menu', default=u'Templates for the current content item.')
    submenuId = 'plone_contentmenu_templates'
    
    order = 11
    extra = {'id' : 'plone-contentmenu-templates'}
    
    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')
    
    def getToolByName(self, tool):
        return getToolByName(getSite(), tool)

    @property
    def action(self):
        folder = self.context
        if not self.context_state.is_structural_folder():
            folder = utils.parent(self.context)
	return folder.absolute_url()

    @memoize
    def available(self):
        actions_tool = self.getToolByName("portal_actions")
        editActions = actions_tool.listActionInfos(object=aq_inner(self.context), categories=('template_buttons', ), max=1)
        wf_tool = self.getToolByName("portal_workflow")

        if self.context.Type() != 'Plone Site' and 'Published' != wf_tool.getInfoFor(self.context, 'review_state'):
            return len(editActions) > 0
        else:
            return False

    def selected(self):
        return False

class TemplateMenu(BrowserMenu):
    implements(IActionsMenu)
    
    
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        portal_state = getMultiAdapter((context, request), name='plone_portal_state')

        actions_tool = getToolByName(aq_inner(context), "portal_actions")
        editActions = actions_tool.listActionInfos(object=aq_inner(context), categories=('template_buttons', ))

        if not editActions:
            return []

        plone_utils = getToolByName(context, 'plone_utils')
        portal_url = portal_state.portal_url()

        for action in editActions:
            if action['allowed']:
                cssClass = 'actionicon-template_buttons-%s' % action['id']
                icon = plone_utils.getIconFor('template__buttons', action['id'], None)
                if icon:
                    icon = '%s/%s' % (portal_url, icon)

                results.append({ 'title'        : action['title'],
                                 'description'  : '',
                                 'action'       : action['url'],
                                 'selected'     : False,
                                 'icon'         : icon,
                                 'extra'        : {'id' : action['id'], 'separator' : None, 'class' : cssClass},
                                 'submenu'      : None,
                                 })

        return results


# CUSTOMIZE ONLY to implement kssIgnore for workflows actions.  Refactor to KSS when applicable #

class WorkflowSubMenuItem(BrowserSubMenuItem):
    implements(IWorkflowSubMenuItem)
    
    MANAGE_SETTINGS_PERMISSION = 'Manage portal'
    
    title = _(u'label_state', default=u'State:')
    submenuId = 'plone_contentmenu_workflow'
    order = 40

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.tools = getMultiAdapter((context, request), name='plone_tools')
        self.context = context
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')

    @property
    def extra(self):
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()
        return {'id'         : 'plone-contentmenu-workflow', 
                'class'      : 'state-%s' % state,
                'state'      : state, 
                'stateTitle' : stateTitle,}
    
    @property
    def description(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return _(u'title_change_state_of_item', default=u'Change the state of this item')
        else:
            return u''

    @property
    def action(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return self.context.absolute_url() + '/content_status_history'
        else:
            return ''
    
    @memoize
    def available(self):
        return (self.context_state.workflow_state() is not None)

    def selected(self):
        return False

    @memoize
    def _manageSettings(self):
        return self.tools.membership().checkPermission(WorkflowSubMenuItem.MANAGE_SETTINGS_PERMISSION, self.context)

    @memoize
    def _transitions(self):
        wf_tool = getToolByName(aq_inner(self.context), "portal_workflow")
        return wf_tool.listActionInfos(object=aq_inner(self.context), max=1)

    @memoize
    def _currentStateTitle(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state
    
class WorkflowMenu(BrowserMenu):
    implements(IWorkflowMenu)
    
    # BBB: These actions (url's) existed in old workflow definitions
    # but were never used. The scripts they reference don't exist in
    # a standard installation. We allow the menu to fail gracefully
    # if these are encountered.
    
    BOGUS_WORKFLOW_ACTIONS = (
        'content_hide_form',
        'content_publish_form',
        'content_reject_form',
        'content_retract_form',
        'content_show_form',
        'content_submit_form',
    )

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []
        context = aq_inner(context)
        
        wf_tool = getToolByName(context, "portal_workflow")
        workflowActions = wf_tool.listActionInfos(object=context)

        for action in workflowActions:
            if action['category'] != 'workflow':
                continue

        locking_info = getMultiAdapter((context, request), name='plone_lock_info')
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        for action in workflowActions:
            if action['category'] != 'workflow':
                continue
            
            actionUrl = action['url']
            if actionUrl == "":
                actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'])

            description = ''
            
            transition = action.get('transition', None)
            if transition is not None:
                description = transition.description
            
            for bogus in self.BOGUS_WORKFLOW_ACTIONS:
                if actionUrl.endswith(bogus):
                    if getattr(context, bogus, None) is None:
                        actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'],)
                    break

            if action['allowed']:
                results.append({ 'title'        : action['title'],
                                 'description'  : description,
                                 'action'       : actionUrl,
                                 'selected'     : False,
                                 'icon'         : None,
                                 'extra'        : {'id' : 'workflow-transition-%s' % action['id'], 'separator' : None, 'class' : 'kssIgnore'},
                                 'submenu'      : None,
                                 })
        
        url = context.absolute_url()
        
        if len(results) > 0:
            results.append({ 'title'         : _(u'label_advanced', default=u'Advanced...'),
                             'description'   : '',
                             'action'        : url + '/content_status_history',
                             'selected'      : False,
                             'icon'          : None,
                             'extra'         : {'id' : '_advanced', 'separator' : 'actionSeparator', 'class' : 'kssIgnore'},
                             'submenu'       : None,
                            })

        if getToolByName(context, 'portal_placeful_workflow', None) is not None:
            results.append({ 'title'         : _(u'workflow_policy', default=u'Policy...'),
                             'description'   : '',
                             'action'        : url + '/placeful_workflow_configuration',
                             'selected'      : False,
                             'icon'          : None,
                             'extra'         : {'id' : '_policy', 'separator' : None, 'class' : 'kssIgnore'},
                             'submenu'       : None,
                            })

        return results
