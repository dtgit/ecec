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
from zope.component import adapts, getUtility, getMultiAdapter
from zope.schema import TextLine, Bool
from schema import ImageLine
from widgets import ImageWidget
from zope.formlib import form
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import ISkinsTool
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.fieldsets import FormFieldsets


def uploadImage(context, filename, file):
    """ Upload an image object. """
    if filename in context.objectIds():
        context.manage_delObjects([filename])
    context.manage_addImage(id=filename, file=file.read())
    

class ILeftSkinGeneralSchema(Interface):

    development_mode = Bool(title=_(u'Development Mode'),
                            description=_(u'In development mode, stylesheets are not merged to composites, '
                                          'and caching and compression of css is disabled. The registry also sends '
                                          'http-headers to prevent browsers from caching the stylesheets. '
                                          'Remember to turn it off as the developmentmode affects performance.'),
                            required=True)

    portal_logo = ImageLine(title=_(u'Portal Logo'),
                            description=_(u'The clickable logo in the top banner. Select '
                                          'the file to be added by clicking the \'Browse\' '
                                          'button. This image should be 360px wide by 63px '
                                          'high to fit within the default layout. The logo will '
                                          'be rendered \'on top of\' the Portal Banner.'),
                            required=False)
                                         
    portal_favicon = ImageLine(title=_(u'Portal Favicon'),
                               description=_(u'The favicon for your portal. Save your image as favicon.ico.'),
                               required=False)
                                         

class ILeftSkinHeaderSchema(Interface):

    portal_banner = ImageLine(title=_(u'Portal Banner'),
                              description=_(u'The top banner of your eduCommons instance. '
                                            'Select the file to be added by clicking the '
                                            '\'Browse\' button. This image should be 2000px '
                                            'wide by 65px high to fit within the default layout.'),
                              required=False)
    
    header_bkg_color = TextLine(title=_(u'Background Color'),
                                description=_(u'The background color of the header.'),
                                required=False)

    header_font_color = TextLine(title=_(u'Font Color'),
                                 description=_(u'The font color of plain text in the header.'),
                                 required=False)

    header_link_color = TextLine(title=_(u'Link Color'),
                                 description=_(u'The color of links in the header.'),
                                 required=False)

    header_active_color = TextLine(title=_(u'Active Link Color'),
                                   description=_(u'The color of selected or highlighted links'),
                                   required=False)

class ILeftSkinTopNavSchema(Interface):

    topnav_background = ImageLine(title=_(u'Background Image'),
                                  description=_(u'You may customize the background of the top navigation '
                                                'elements (home, courses, help, about OCW) by uploading a '
                                                'background image. For non-tiling images, the size should '
                                                'be 2000px wide by 28px high.'),
                                  required=False)
    
    topnav_bkg_color = TextLine(title=_(u'Background Color'),
                                description=_(u'The background color of the top navigation bar.'),
                                required=False)

    topnav_font_color = TextLine(title=_(u'Font Color'),
                                 description=_(u'The font color for the top navigation bar.'),
                                 required=False)

    topnav_link_color = TextLine(title=_(u'Link Color'),
                                 description=_(u'The color of links in the top navigation bar'),
                                 required=False)

    topnav_active_color = TextLine(title=_(u'Active Link Color'),
                                   description=_(u'The color of selected or highlighted links.'),
                                   required=False)

class ILeftSkinLeftNavSchema(Interface):

    leftnav_background = ImageLine(title=_(u'Background Image'),
                                   description=_(u'The background image for the Left Hand Column. '
                                                 'Select the file to be added by clicking the '
                                                 '\'Browse\' button. This image should be 150px wide '
                                                 'by 10px high to fit within the default layout.'),
                                   required=False)
    
    leftnav_bkg_color = TextLine(title=_(u'Background Color'),
                                 description=_(u'The background color of the left navigation section.'),
                                 required=False)

    leftnav_font_color = TextLine(title=_(u'Font Color'),
                                  description=_(u'The font color for the left navigation section.'),
                                  required=False)

    leftnav_link_color = TextLine(title=_(u'Link Color'),
                                  description=_(u'The color of links in the left navigation section.'),
                                  required=False)

    leftnav_active_color = TextLine(title=_(u'Active Link Color'),
                                    description=_(u'The color of the selected or highlighted links.'),
                                    required=False)

class ILeftSkinContentSchema(Interface):
    
    content_bkg_color = TextLine(title=_(u'Background Color'),
                                 description=_(u'The background color for this section.'),
                                 required=False)

    content_font_color = TextLine(title=_(u'Font Color'),
                                  description=_(u'The link color for this section.'),
                                  required=False)

    content_link_color = TextLine(title=_(u'Link Color'),
                                  description=_(u'The color of links in this section.'),
                                  required=False)

    content_active_color = TextLine(title=_(u'Active Link Color'),
                                    description=_(u'The color of selected or highlighted links '
                                                  'in this section.'),
                                    required=False)

class ILeftSkinSchema(ILeftSkinGeneralSchema,
                      ILeftSkinHeaderSchema, 
                      ILeftSkinTopNavSchema, 
                      ILeftSkinLeftNavSchema,
                      ILeftSkinContentSchema):
    """ Combine schemas in tab form. """


class LeftSkinControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ILeftSkinSchema)

    def __init__(self, context):
        super(LeftSkinControlPanelAdapter, self).__init__(context)
        # look up the tool properly at some point, getUtility(ISkinsTool)
        # fails for some reason, until then just access it directly
        self.skins = context.portal_skins.custom
        self.props = context.portal_skins.custom.base_properties
        self.css = context.portal_css

    # General settings

    def get_development_mode(self):
        return self.css.getDebugMode()

    def set_development_mode(self, mode):
        self.css.setDebugMode(mode)

    development_mode = property(get_development_mode, set_development_mode)

    def get_portal_logo(self):
        return self.props.getProperty('logoName')

    def set_portal_logo(self, file):
        if file:
            uploadImage(self.skins, 'logo.gif', file)

    portal_logo = property(get_portal_logo, set_portal_logo)

    def get_portal_favicon(self):
        return self.props.getProperty('faviconName')

    def set_portal_favicon(self, file):
        if file:
            uploadImage(self.skins, 'favicon.ico', file)

    portal_favicon = property(get_portal_favicon, set_portal_favicon)

    # Header settings

    def get_portal_banner(self):
        return self.props.getProperty('portalHeaderBackgroundImage')

    def set_portal_banner(self, file):
        if file:
            uploadImage(self.skins, 'headerBackground.png', file)

    portal_banner = property(get_portal_banner, set_portal_banner)
        
    def get_header_bkg_color(self):
        return self.props.getProperty('portalHeaderBackgroundColor')

    def set_header_bkg_color(self, color):
        self.props.manage_changeProperties(portalHeaderBackgroundColor=color.encode('ascii'))

    header_bkg_color = property(get_header_bkg_color, set_header_bkg_color)

    def get_header_font_color(self):
        return self.props.getProperty('portalHeaderFontColor')

    def set_header_font_color(self, color):
        self.props.manage_changeProperties(portalHeaderFontColor=color.encode('ascii'))

    header_font_color = property(get_header_font_color, set_header_font_color)

    def get_header_link_color(self):
        return self.props.getProperty('portalHeaderLinkColor')

    def set_header_link_color(self, color):
        self.props.manage_changeProperties(portalHeaderLinkColor=color.encode('ascii'))

    header_link_color = property(get_header_link_color, set_header_link_color)

    def get_header_active_color(self):
        return self.props.getProperty('portalHeaderActiveColor')

    def set_header_active_color(self, color):
        self.props.manage_changeProperties(portalHeaderActiveColor=color.encode('ascii'))

    header_active_color = property(get_header_active_color, set_header_active_color)

    # Top Navigation Bar settings

    def get_topnav_background(self):
        return self.props.getProperty('portalTopNavBackgroundImage')

    def set_topnav_background(self, file):
        if file:
            uploadImage(self.skins, 'topNavBackground.png', file)

    topnav_background = property(get_topnav_background, set_topnav_background)

    def get_topnav_bkg_color(self):
        return self.props.getProperty('portalTopNavBackgroundColor')

    def set_topnav_bkg_color(self, color):
        color = color.encode('ascii')
        self.props.manage_changeProperties(portalTopNavBackgroundColor=color)
        self.props.manage_changeProperties(globalBorderColor=color)

    topnav_bkg_color = property(get_topnav_bkg_color, set_topnav_bkg_color)

    def get_topnav_font_color(self):
        return self.props.getProperty('portalTopNavFontColor')

    def set_topnav_font_color(self, color):
        self.props.manage_changeProperties(portalTopNavFontColor=color.encode('ascii'))

    topnav_font_color = property(get_topnav_font_color, set_topnav_font_color)

    def get_topnav_link_color(self):
        return self.props.getProperty('portalTopNavLinkColor')

    def set_topnav_link_color(self, color):
        self.props.manage_changeProperties(portalTopNavLinkColor=color.encode('ascii'))

    topnav_link_color = property(get_topnav_link_color, set_topnav_link_color)

    def get_topnav_active_color(self):
        return self.props.getProperty('portalTopNavActiveColor')

    def set_topnav_active_color(self, color):
        self.props.manage_changeProperties(portalTopNavActiveColor=color.encode('ascii'))

    topnav_active_color = property(get_topnav_active_color, set_topnav_active_color)

    # Left Navigation settings

    def get_leftnav_background(self):
        return self.props.getProperty('portalColumnOneBackgroundImage')

    def set_leftnav_background(self, file):
        if file:
            uploadImage(self.skins, 'columnOneBackground.png', file)

    leftnav_background = property(get_leftnav_background, set_leftnav_background)

    def get_leftnav_bkg_color(self):
        return self.props.getProperty('portalColumnOneBackgroundColor')

    def set_leftnav_bkg_color(self, color):
        self.props.manage_changeProperties(portalColumnOneBackgroundColor=color.encode('ascii'))

    leftnav_bkg_color = property(get_leftnav_bkg_color, set_leftnav_bkg_color)

    def get_leftnav_font_color(self):
        return self.props.getProperty('portalColumnOneFontColor')

    def set_leftnav_font_color(self, color):
        self.props.manage_changeProperties(portalColumnOneFontColor=color.encode('ascii'))

    leftnav_font_color = property(get_leftnav_font_color, set_leftnav_font_color)

    def get_leftnav_link_color(self):
        return self.props.getProperty('portalColumnOneLinkColor')

    def set_leftnav_link_color(self, color):
        self.props.manage_changeProperties(portalColumnOneLinkColor=color.encode('ascii'))

    leftnav_link_color = property(get_leftnav_link_color, set_leftnav_link_color)

    def get_leftnav_active_color(self):
        return self.props.getProperty('portalColumnOneActiveColor')

    def set_leftnav_active_color(self, color):
        self.props.manage_changeProperties(portalColumnOneActiveColor=color.encode('ascii'))

    leftnav_active_color = property(get_leftnav_active_color, set_leftnav_active_color)

    # Content settings

    def get_content_bkg_color(self):
        return self.props.getProperty('backgroundColor')

    def set_content_bkg_color(self, color):
        self.props.manage_changeProperties(backgroundColor=color.encode('ascii'))

    content_bkg_color = property(get_content_bkg_color, set_content_bkg_color)

    def get_content_font_color(self):
        return self.props.getProperty('fontColor')

    def set_content_font_color(self):
        self.props.manage_changeProperties(fontColor=color.encode('ascii'))

    content_font_color = property(get_content_font_color, set_content_font_color)

    def get_content_link_color(self):
        return self.props.getProperty('linkColor')

    def set_content_link_color(self, color):
        self.props.manage_changeProperties(linkColor=color.encode('ascii'))

    content_link_color = property(get_content_link_color, set_content_link_color)

    def get_content_active_color(self):
        return self.props.getProperty('linkActiveColor')

    def set_content_active_color(self, color):
        self.props.manage_changeProperties(linkActiveColor=color.encode('ascii'))

    content_active_color = property(get_content_active_color, set_content_active_color)

    def clearAllSettings(self):
        """ Remove all customizations. """
        objs = self.skins.objectIds()
        custom = ['logo.gif',
                  'favicon.ico',
                  'headerBackground.png', 
                  'topNavBackground.png',
                  'columnOneBackground.png',
                  'base_properties']
        self.skins.manage_delObjects(filter(lambda x:x in objs, custom))

        stool = self.context.portal_skins
        stool.leftskin.base_properties.manage_doCustomize(folder_path='custom')
        

generalset = FormFieldsets(ILeftSkinGeneralSchema)
generalset['portal_logo'].custom_widget = ImageWidget
generalset['portal_favicon'].custom_widget = ImageWidget
generalset.id = 'leftskinGeneralSchema'
generalset.description = _(u'General settings for the Left Skin Theme.')
generalset.label = _(u'General')

headerset = FormFieldsets(ILeftSkinHeaderSchema)
headerset['portal_banner'].custom_widget = ImageWidget
headerset.id = 'leftSkinHeaderSchema'
headerset.description = _(u'Skin settings for the portal header which appears '
                          'at the top of the page.')
headerset.label = _(u'Header')

topnavset = FormFieldsets(ILeftSkinTopNavSchema)
topnavset['topnav_background'].custom_widget = ImageWidget
topnavset.id = 'leftSkinTopNavSchema'
topnavset.description = _(u'Skin settings for the top navigation bar which '
                          'appears below the portal header.')
topnavset.label = _(u'Top Nav Bar')

leftnavset = FormFieldsets(ILeftSkinLeftNavSchema)
leftnavset['leftnav_background'].custom_widget = ImageWidget
leftnavset.id = 'leftSkinleftNavSchema'
leftnavset.description = _(u'Skin settings for the left navigation section.')
leftnavset.label = _(u'Left Nav')

contentset = FormFieldsets(ILeftSkinContentSchema)
contentset.id = 'leftSkinContentSchema'
contentset.description = _(u'Skin settins for the content section.')
contentset.label = _(u'Content')


class LeftSkinControlPanel(ControlPanelForm):
    
    form_fields = FormFieldsets(generalset, headerset, topnavset, leftnavset, contentset)

    label = _(u'Left Skin Settings')
    description = _(u'Settings that affect the left skin theme. '
                    'Remember to clear you browser\'s cache in order '
                    'to see the changes made in this control panel.')
    form_name = _(u'Left Skin Settings')

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_reset_default', default=u'Reset to Default'),
                 validator=null_validator,
                 name=u'Reset to Default')
    def handle_reset(self, action, data):
        if self.adapters.has_key('ILeftSkinGeneralSchema'):
            self.adapters['ILeftSkinGeneralSchema'].clearAllSettings()
            self.status = _('Changes Saved')
        else:
            self.status = _('No changes made.')


    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
        



