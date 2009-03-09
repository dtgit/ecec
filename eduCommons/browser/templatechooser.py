##################################################################################
#    Copyright (C) 2007 Utah State University, All rights reserved.          
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

__author__ = 'David Ray, John Thomas, Brent Lambert'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]


from zope.formlib.form import PageForm, FormFields, action
from zope.app.form.interfaces import WidgetInputError
from zope.component import getMultiAdapter
from Products.PageTemplates import PageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from interfaces import ITemplateForm

from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget

from zope.interface import implements
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary



def templateVocabulary(context):
    template_actions = context.portal_actions.listActionInfos(object=context, categories=('template_buttons'))
    items = ()
    for template_action in template_actions:
        id = template_action['id']
        title = str(template_action['title'])
        items += (title, id), 
        
    return SimpleVocabulary.fromItems(items)


class TemplateForm(PageForm):
    """ A form for selecting templates on objects """

    form_fields = FormFields(ITemplateForm)
    form_fields['template'].custom_widget = ChoiceRadioWidget

    label = u'Template Chooser'
    description = u'Preview and choose templates for your content object'


    @action(_(u'label_submit', default=u'Apply Template'), 
            name=u'Submit')
    def action_submit(self, action, data):
        # Apply the template
        if data.has_key('template') and data['template']:
            context = self.context
            template = '@@%s' % data['template']
            template = context.restrictedTraverse(str(template))
            text = template(context)
            context.setText(text)
            if data['template'] in ['syllabus_view']:
                context.setPresentation(True)
            self.request.response.redirect('view')

        return ''

    
