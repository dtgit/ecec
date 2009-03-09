from zope.interface import implements
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IOerRecommenderPortlet(IPortletDataProvider):
    """ A OER Recommender Portlet. """

class Assignment(base.Assignment):
    """Assignment for OER Recommender Portlet """

    implements(IOerRecommenderPortlet)

    title = _(u'OER Recommender Portlet')


class Renderer(base.Renderer):
    """ Render the OER Portlet """
    render = ViewPageTemplateFile('oerrecommender.pt')


    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.props = self.context.portal_properties.educommons_properties

    @property
    def available(self):
        return self.props.oerrecommender_enabled



class AddForm(base.NullAddForm):
    form_fields = form.Fields(IOerRecommenderPortlet)
    
    def create(self):
        return Assignment()


