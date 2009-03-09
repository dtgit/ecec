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


from zope.interface import implements, Interface
from zope.component import adapts
from Products.Five.formlib.formbase import PageForm
from zope.formlib.form import Fields, FormFields, action
from zope.schema import TextLine
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ICourseBuilderPortlet(IPortletDataProvider):
    """ A course building portlet """


class Assignment(base.Assignment):
    """ Assignment """

    implements(ICourseBuilderPortlet)

    title = _(u'Course Builder Portlet')


class Renderer(base.Renderer):
    """ Renderer """

    render = ViewPageTemplateFile('coursebuilder.pt')

    def __init__(self, context, request, view, manager, data):
        super(base.Renderer, self).__init__(context, request, view, manager, data)
        self.context = context

    @property
    def available(self):
        roles = self.context.portal_membership.getAuthenticatedMember().getRoles()
        if 'Contributor' in roles or 'Producer' in roles or 'Administrator' in roles or 'Manager' in roles:
            return True
        return False

    def getDivisionDescriptor(self):
        return self.context.portal_properties.educommons_properties.getProperty('division_descriptor')

    def getDivisions(self):
        divs =  ['Mathematics', 'Computer Science', 'Instructional Technology',
                 'Decorating']
        
        return divs

    def getTemplates(self):
        return ['Syllabus', 'Course Schedule', 'About the Professor']


class AddForm(base.NullAddForm):
    """ Add Form """

    form_fields = Fields(ICourseBuilderPortlet)

    def create(self):
        return Assignment()


