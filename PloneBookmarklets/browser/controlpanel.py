##################################################################################
#    Copyright (C) 2004-2007 Utah State University, All rights reserved.          
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

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]

from zope.interface import Interface, implements
from zope.component import adapts, getUtility
from zope.formlib import form
from zope.app.form.interfaces import WidgetInputError
from plone.fieldsets import FormFieldsets
from zope.schema import TextLine, Choice, Tuple
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget 



def validate_new_site(form, action, data):
    """ Validate the new bookmarking site data. """
    errors = form.validate(action, data)
    if errors:
        return errors
    if data['new_site_name']:
        if not data['new_site_url']:
            ew = form.widgets.get('new_site_url')
            ew._error = WidgetInputError(form.context.__name__, ew.label, _('Missing site url'))
            return ew._error
        if not data['new_site_icon']:
            ew = form.widgets.get('new_site_icon')
            ew._error = WidgetInputError(form.context.__name__, ew.label, _('Missing site icon'))
            return ew._error


    


def availablevocab(context):
    props = getToolByName(context, 'portal_properties')
    available = props.bookmarklets_properties.available_sites
    sites = []
    for x in available:
        value = getattr(props.bookmarklets_properties, x)[0], x
        sites.append(value)
    return SimpleVocabulary.fromItems(sites)

class IbookmarkletsSchema(Interface):
    """ The view for the PloneBookmarklets control panel  """
    displayed_sites = Tuple(title=_(u'Displayed Bookmarklets'),
                            description=_(u'Choose which bookmarking services are displayed'),
                            required=True,
                            missing_value=tuple(),
                            value_type=Choice(vocabulary='bookmarklets.availablevocab'))

class IbookmarkletsNewSiteForm(Interface):
    """  The view for the add new bookmarklet site form """

    new_site_name = TextLine(title=_(u'Bookmarking Site Name'),
                                description=_(u'The name of the bookmarking site.'),
                                required=False)

    new_site_url = TextLine(title=_(u'Bookmarking Site Referring URL'),
                               description=_(u'The URL to which the bookmark is sent, '
                                             'include the following supported parameters: URL, ENCODED_TITLE. '
                                             'For example, http://del.icio.us/post?url=URL&amp;title=ENCODED_TITLE'),
                               required=False)

    new_site_icon = TextLine(title=_(u'Bookmarking Site Icon'),
                                description=_(u'The URL pointer to an image associated with the boomkarking site.'),
                                required=False)

class IbookmarkletsControlPanel(IbookmarkletsSchema, IbookmarkletsNewSiteForm):
    """ Combined control panel and new site form. """


class bookmarkletsControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel Adapter """

    adapts(IPloneSiteRoot)
    implements(IbookmarkletsControlPanel)

    temp_site = ['', '', '']

    def __init__(self, context):
        super(bookmarkletsControlPanelAdapter, self).__init__(context)
        self.props = getUtility(IPropertiesTool)
        self.bmprops = self.props.bookmarklets_properties

    def get_displayed_sites(self):
        return self.bmprops.displayed_sites

    def set_displayed_sites(self, displayedsites):
        self.bmprops.displayed_sites = displayedsites

    displayed_sites = property(get_displayed_sites, set_displayed_sites)

    # User the new site fields to generate a new site, not set individual properties

    def get_nothing(self):
        return ''

    def set_nothing(self, param):
        pass

    new_site_name = property(get_nothing, set_nothing)
    new_site_url = property(get_nothing, set_nothing)
    new_site_icon = property(get_nothing, set_nothing)

    def setNewBookmarkingSite(self, name, url, icon):
        """ Set a new bookmarking site  """
        new_site = [name, '', '']
        if url:
            new_site[1] = url
        if icon:
            new_site[2] = icon

        site_id = ''.join(name.lower().split())
        self.bmprops.manage_addProperty(site_id, new_site, 'lines')
        self.bmprops.manage_changeProperties(displayed_sites=list(self.bmprops.displayed_sites) + [site_id])
        self.bmprops.manage_changeProperties(available_sites=list(self.bmprops.available_sites) + [site_id])

settingsset = FormFieldsets(IbookmarkletsSchema)
settingsset.id = 'bookmarkletssettings'
settingsset.label = _(u'Settings')

newsiteset = FormFieldsets(IbookmarkletsNewSiteForm)
newsiteset.id = 'bookmarkletsnewsite'
newsiteset.label = _('New Site')

class BookmarkletsControlPanel(ControlPanelForm):

    implements(IbookmarkletsControlPanel)
    form_fields = FormFieldsets(settingsset, newsiteset)
    form_fields['displayed_sites'].custom_widget = MultiCheckBoxVocabularyWidget
    

    label = _(u'PloneBookmarklets Settings')
    description = _(u'Settings which controls the bookmarking sites to be displayed.')
    form_name = _(u'PloneBookmarklets Settings')

    @form.action(_(u'label_save', default=u'Save'), validator=validate_new_site, name=u'save')
    def handle_edit_action(self, action, data):
        #apply form changes
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            #if there is a new site in the form, add it to the properties page
            if data.has_key('new_site_name') and data['new_site_name']:
                ad = self.adapters[IbookmarkletsNewSiteForm]
                ad.setNewBookmarkingSite(data['new_site_name'],
                                         data['new_site_url'],
                                         data['new_site_icon'])

            self.status = _("Changes saved.")
            self._on_save(data)
            self.request['fieldset.current'] = u'fieldsetlegend-bookmarkletssettings'
        else:
            self.status = _("No changes made.")
            
