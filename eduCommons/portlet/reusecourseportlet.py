from zope.interface import implements
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from Products.eduCommons.utilities.interfaces import IECUtility

class IReuseCoursePortlet(IPortletDataProvider):
    """ A portlet that facilitates course reuse. """


class Assignment(base.Assignment):

    implements(IReuseCoursePortlet)
    title = _(u'Reuse Course')

    
class Renderer(base.Renderer):

    render = ViewPageTemplateFile('reusecourse.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.ecutil = getUtility(IECUtility)
        self.ecparent = self.ecutil.FindECParent(context)

    @property
    def available(self):
        #Only make visible if Course is Published and IMS Package exists
        #IMS pkg name
        wf_tool = self.ecparent.portal_workflow
        ims_pkg = ''
        ims_pkg = '%s.zip' % self.ecparent.id
        
        if self.ecparent.Type() == 'Course':
            if 'Published' == wf_tool.getInfoFor(self.ecparent, 'review_state') and hasattr(self.ecparent, ims_pkg):
                if 'Published' == wf_tool.getInfoFor(getattr(self.ecparent, ims_pkg), 'review_state'):
                    return True
        return False

    @property
    def ims_id(self):
        return '%s.zip' % self.ecparent.id


class AddForm(base.NullAddForm):

    form_fields = form.Fields(IReuseCoursePortlet)

    def create(self):
        return Assignment()
