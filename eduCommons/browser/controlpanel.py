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
from zope.formlib.form import FormFields
from zope.schema import TextLine, Bool
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.controlpanel.form import ControlPanelForm


class IeduCommonsSchema(Interface):
    
    division_descriptor = TextLine(title=_(u'Division Descriptor'),
                                   description=_(u'A descriptor that describes how your '
                                                 'academic institution is divided. Typically '
                                                 'this will be "Departments" or "Divisions."'),
                                   required=True)

    course_descriptor = TextLine(title=_(u'Course Descriptor'),
                                 description=_(u'A descriptor that describes courses '
                                               'in your institution.'),
                                 required=True)

    oerrecommender_enabled = Bool(title=_(u'OER Recommender'),
                                  description=_(u'Enable the display of the OER Recommender Portlet for Course objects and sub-objects.'),
                                  default=False,
                                  required=True)

    reusecourse_enabled = Bool(title=_(u'Allow Reuse Course Export'),
                                  description=_(u'Enable the display of the course export link for Course objects and sub-objects.'),
                                  default=False,
                                  required=True)


    reusecourse_instance = TextLine(title=_('Reuse Course Portal'),
                                    description=_(u'The URL to the eduCommons instance utilized by the Reuse Course portlet.'),
                                    required=True)


class eduCommonsControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel Adapter """

    adapts(IPloneSiteRoot)
    implements(IeduCommonsSchema)

    def __init__(self, context):
        super(eduCommonsControlPanelAdapter, self).__init__(context)
        self.props = getUtility(IPropertiesTool)
        self.ecprops = self.props.educommons_properties

    def get_division_descriptor(self):
        return self.ecprops.getProperty('division_descriptor')

    def set_division_descriptor(self, descriptor):
        self.ecprops.manage_changeProperties(division_descriptor=descriptor)

    def get_course_descriptor(self):
        return self.ecprops.getProperty('course_descriptor')

    def set_course_descriptor(self, descriptor):
        self.ecprops.manage_changeProperties(course_descriptor=descriptor)

    def get_oerrecommender_enabled(self):
        return self.ecprops.getProperty('oerrecommender_enabled')

    def set_oerrecommender_enabled(self, oerrecommender):
        self.ecprops.manage_changeProperties(oerrecommender_enabled=oerrecommender)

    def get_reusecourse_enabled(self):
        return self.ecprops.getProperty('reusecourse_enabled')

    def set_reusecourse_enabled(self, reusecourse_enable):
        self.ecprops.manage_changeProperties(reusecourse_enabled=reusecourse_enable)

    def get_reusecourse_instance(self):
        return self.ecprops.getProperty('reusecourse_instance')

    def set_reusecourse_instance(self, reusecourse):
        self.ecprops.manage_changeProperties(reusecourse_instance=reusecourse)



    course_descriptor = property(get_course_descriptor, set_course_descriptor)
    division_descriptor = property(get_division_descriptor, set_division_descriptor)
    oerrecommender_enabled = property(get_oerrecommender_enabled, set_oerrecommender_enabled)
    reusecourse_enabled = property(get_reusecourse_enabled, set_reusecourse_enabled)
    reusecourse_instance = property(get_reusecourse_instance, set_reusecourse_instance)

class eduCommonsControlPanel(ControlPanelForm):

    form_fields = FormFields(IeduCommonsSchema)
    
    label = _(u'eduCommons Settings')
    description = _(u'Settings which control how eduCommons looks and functions.')
    form_name = _(u'eduCommons Settings')
