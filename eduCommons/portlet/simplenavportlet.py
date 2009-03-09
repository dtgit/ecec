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


from zope.interface import implements
from zope.component import getUtility
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.eduCommons.utilities.interfaces import IECUtility


class ISimpleNavPortlet(IPortletDataProvider):
    """ A simple navigation portlet. """


class Assignment(base.Assignment):

    implements(ISimpleNavPortlet)

    title = _(u'eduCommons Navigation')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('simplenav.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.ecutil = getUtility(IECUtility)
        self.ecparent = self.ecutil.FindECParent(context)

    def getNavObjects(self):
        """ Get navigable objects. """
        if self.isCourseObject():
            path = {'path':{'query':'/'.join(self.ecparent.getPhysicalPath())+'/'},
                    'getExcludeFromNav':False,
                    'sort_on':'getObjPositionInCourse'}
            brains = self.context.portal_catalog.searchResults(path)
        else:
            brains = self.context.portal_catalog.searchResults(Type='Division',
                                                               sort_on='sortable_title')
        return [obj for obj in brains if not getattr(obj.aq_explicit, 'exclude_from_nav', True)]

    def isCourseObject(self):
        """ Check if this object is in a course. """
        return 'Course' == self.ecparent.Type()

    def isSelected(self, item):
        """ Check if the navigaion item is the one being displayed. """
        if '/'.join(item.getPath().split('/')[1:]) == self.context.virtual_url_path():
            return 'portletItem portletItemSelected'
        else:
            return 'portletItem'
        
    def getDescriptor(self):
        ecprops = self.context.portal_url.portal_properties.educommons_properties
        if self.isCourseObject():
            return ecprops.course_descriptor + ' ' + _(u'Contents')
        else:
            return ecprops.division_descriptor
            
    def get_view_url(self, item):
        props = self.context.portal_url.portal_properties
        stp = props.site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings', ())
        
        item_url = item.getURL()

        if item.portal_type in view_action_types:
            item_url += '/view'
        elif item.portal_type == 'Link':
            item_url = item.getRemoteUrl

        return item_url
        

class AddForm(base.NullAddForm):
    form_fields = form.Fields(ISimpleNavPortlet)
    
    def create(self):
        return Assignment()


